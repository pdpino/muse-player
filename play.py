#!/usr/bin/env python
"""Play muse data

Connects with a muse (2016) device, stream the data through a text/event-stream and save the data to a csv"""

from time import sleep, time
from collections import deque
import numpy as np
import pandas as pd
import argparse
import threading
import signal
from flask import Response, Flask   # Stream data to client
from flask_cors import CORS
from muse import Muse
from basic.data_manager import save_data
import basic


# Next TODOs:
# TODO: handle when muse turns off
# TODO: despues de un rato vaciar listas full_data y full_time, se llenan mucho # opcion para guardarlas como dump o no
# XXX: ver cuando se desconecta: https://stackoverflow.com/questions/18511119/stop-processing-flask-route-if-request-aborted
# IDEA: probar qué tanta información se pierde en mandar promedio, un dato o todos
    # calcular cov o dispersion de 12 samples (?)

# Not urgent
# TODO: ordenar README_develop seccion "headband en estado normal" y "en estado extraño"

class DataContainer(object):
    """Contains the data produced by Muse, gives it to Flask to stream it"""

    def __init__(self, maxsize=10, yield_function=None):
        # All the data
        self._full_time = []
        self._full_data = []

        # Queues para stream de datos, # thread safe
        self._q_time = deque(maxlen=maxsize)
        self._q_data = deque(maxlen=maxsize)
        self.lock = threading.Lock()

        # Yielder
        self._yielder = yield_function

    """Stream methods"""
    def incoming_data(self, timestamps, data):
        """Process the incoming data."""
        # Add to full lists
        self._full_time.append(timestamps)
        self._full_data.append(data)

        # Add to queue
        with self.lock:
            self._q_time.append(timestamps)
            self._q_data.append(data)

    def data_generator(self, n_data):
        """Generator to stream the data."""
        if self._yielder is None:
            basic.perror("Can't stream the data without a yielder")
            return

        with self.lock:
            # Drop old data in queue
            self._q_time.clear()
            self._q_data.clear()
            t_init = time() # Set an initial time as marker

        while True:
            self.lock.acquire()
            if len(self._q_time) == 0 or len(self._q_data) == 0: # NOTE: both lengths should always be the same
                self.lock.release()
                continue

            t = self._q_time.popleft()
            d = self._q_data.popleft()
            self.lock.release()

            yield from self._yielder(t, t_init, d, n_data)

class EEGContainer(DataContainer):
    """Contains the eeg data produced by Muse"""
    def get_running_time(self):
        """Return the running time"""
        if len(self._full_time) == 0:
            return 0

        t_end = self._full_time[-1][-1]
        t_init = self._full_time[0][0]
        return t_end - t_init

    def _normalize_time(self):
        """Receive a list of np arrays of timestamps. Return the concatenated and normalized (substract initial time) np array"""

        # Concat y normalizar timestamps
        timestamps = np.concatenate(self._full_time)
        return timestamps - timestamps[0]

    def _normalize_data(self):
        """Return the data concatenated"""
        return np.concatenate(self._full_data, 1).T

    def save_csv(self, fname, subfolder=None, suffix=None):
        """Preprocess the data and save it to a csv."""
        if len(self._full_time) == 0 or len(self._full_data) == 0:
            return


        # Concatenar data
        timestamps = normalize_time(self._full_time)
        data = normalize_data(self._full_data)

        # Juntar en dataframe
        res = pd.DataFrame(data=data, columns=['TP9', 'AF7', 'AF8', 'TP10', 'Right AUX'])
        res['timestamps'] = timestamps

        # Guardar a csv
        save_data(res, fname, subfolder, suffix)

class EEGyielder(object):
    """Yield functions to stream the data in the desired way.

    Assumes that the shape of the data is:
    len(t) == 12
    d.shape == (5, 12)"""

    # String para hacer yield
    # EEG envia (timestamp, ch0, ch1, ch2, ch3, ch4)
    yield_string = "data: {}, {}, {}, {}, {}, {}\n\n"

    @staticmethod
    def _get_data_mean(t, t_init, data, dummy=None):
        """Yield the mean in the 12 samples for each channel separately."""
        yield EEGyielder.yield_string.format( \
                t.mean() - t_init, \
                data[0].mean(), \
                data[1].mean(), \
                data[2].mean(), \
                data[3].mean(), \
                data[4].mean() )

    @staticmethod
    def _get_data_max(t, t_init, data, dummy=None):
        """Yield the max of the 12 samples for each channel separately"""
        # NOTE: use tt.max(), tt.mean()?
        yield EEGyielder.yield_string.format( \
                t.max() - t_init, \
                data[0].max(), \
                data[1].max(), \
                data[2].max(), \
                data[3].max(), \
                data[4].max() )

    @staticmethod
    def _get_data_min(t, t_init, data, dummy=None):
        """Yield the min of the 12 samples for each channel separately"""
        yield EEGyielder.yield_string.format( \
                t.min() - t_init, \
                data[0].min(), \
                data[1].min(), \
                data[2].min(), \
                data[3].min(), \
                data[4].min() )

    @staticmethod
    def _get_data_n(t, t_init, data, n):
        """Yield n out of the 12 samples."""
        for i in range(n):
            tt = t[i] - t_init
            yield EEGyielder.yield_string.format(
                tt, \
                data[0][i], \
                data[1][i], \
                data[2][i], \
                data[3][i], \
                data[4][i] )

    @staticmethod
    def get_yielder(mode):
        """Return the selected yielder function"""
        # Available yielders
        yielders = {
            "mean": EEGyielder._get_data_mean,
            "min": EEGyielder._get_data_min,
            "max": EEGyielder._get_data_max,
            "n": EEGyielder._get_data_n
            }

        try:
            yielder = yielders[mode]
        except KeyError:
            basic.perror("yielder: {} not found".format(mode), force_continue=True)
            yielder = EEGyielder._get_data_n # Default

        return yielder


def parse_args():
    """Create a parser, get the args, return them preprocessed."""
    def create_parser():
        """ Create the console arguments parser"""
        parser = argparse.ArgumentParser(description='Send muse data to client and save to .csv',
                            usage='%(prog)s [options]', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        parser.add_argument('-t', '--time', default=None, type=float,
                            help="Seconds to record data (aprox). If none, stop listening only when interrupted")

        group_bconn = parser.add_argument_group(title="Bluetooth connection", description=None)
        group_bconn.add_argument('-i', '--interface', default=None, type=str,
                            help="Bluetooth interface, e.g: hci0, hci1")
        group_bconn.add_argument('-a', '--address', default="00:55:DA:B3:20:D7", type=str,
                            help="Device's MAC address")

        group_data = parser.add_argument_group(title="Data",
                            description="Parameters of the processed and streamed data")
        group_data.add_argument('--stream_mode', choices=["mean", "n", "max", "min"], type=str, default="n",
                            help="Choose what part of the data to yield to the client. If 'n' is selected consider providing a --stream_n argument as well") # TODO: add to README
        group_data.add_argument('--stream_n', default=1, type=int,
                            help="If --stream_mode n is selected, define the amount of data to yield")
        group_data.add_argument('--nsub', default=None, type=int,
                            help="Normalize substractor. Number to substract to the raw data when incoming, before the factor. If None, it will use the muse module default value") # TODO: add to README
        group_data.add_argument('--nfactor', default=None, type=int,
                            help="Normalize factor. Number to multiply the raw data when incoming. If None, it will use the muse module default value") # TODO: add to README


        group_save = parser.add_argument_group(title="File arguments", description=None)
        group_save.add_argument('-s', '--save', action="store_true",
                            help="Save a .csv with the raw data")
        group_save.add_argument('-f', '--fname', default="dump", type=str,
                            help="Name to store the .csv file")
        group_save.add_argument('--subfolder', default=None, type=str,
                            help="Subfolder to save the .csv file")
        # group_save.add_argument('--save_stream', action="store_true",
        #                     help="Save the data that is streamed on different files")


        group_sconn = parser.add_argument_group(title="Stream connection", description=None)
        group_sconn.add_argument('--ip', default="localhost", type=str,
                            help="Host ip to do the streaming")
        group_sconn.add_argument('--port', default=8889, type=int,
                            help="Port to send the data to")
        group_sconn.add_argument('--url', default="/data/muse", type=str,
                            help="Path in the client to send the data, so it will be sent to 'http://ip:port/url'")


        return parser

    parser = create_parser()
    args = parser.parse_args()

    # Assure a url well formed
    args.url = basic.assure_startswith(args.url, "/")

    # Cap the amount of data to yield
    if args.stream_n > 12:
        args.stream_n = 12
    elif args.stream_n <= 0:
        args.stream_n = 1

    return args

def main():
    """Connect with muse and stream the data"""
    # Get arguments
    args = parse_args()

    # Container for the incoming data
    eeg_container = EEGContainer(yield_function=EEGyielder.get_yielder(args.stream_mode))

    # Conectar muse
    muse = Muse(args.address, eeg_container.incoming_data, norm_factor=args.nfactor, norm_sub=args.nsub)
    muse.connect(interface=args.interface)

    # Init Flask
    app = Flask(__name__) # iniciar app de Flask
    CORS(app) # para que cliente pueda acceder a este puerto
    stream = threading.Thread(target=app.run, kwargs={"host":args.ip, "port":args.port})
    stream.daemon = True

    # Catch ctrl-c
    catcher = basic.SignalCatcher()
    signal.signal(signal.SIGINT, catcher.signal_handler)


    # Connect EEGdata
    @app.route(args.url)
    def stream_eeg():
        """Return a generator to stream the data """
        return Response(eeg_container.data_generator(args.stream_n), mimetype="text/event-stream")


    ## Iniciar
    muse.start()
    stream.start()

    print("Started receiving data")
    if args.time is None:
        while catcher.keep_running():
            sleep(1)
    else:
        print("\tfor (aprox) {} seconds".format(args.time)) # HACK
        sleep(args.time)

    muse.stop()
    muse.disconnect()
    print("Stopped receiving muse data")

    # Imprimir mensajes que recibio Muse en todo el proceso
    # muse.print_msgs()

    # Print running time
    print("\tReceived data for {:.2f} seconds".format(eeg_container.get_running_time()))

    if args.save:
        eeg_container.save_csv(args.fname, subfolder=args.subfolder)

    return 0


if __name__ == "__main__":
    main()
