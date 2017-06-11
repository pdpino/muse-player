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
# IDEA: probar qué tanta información se pierde en mandar promedio, un dato o todos
    # calcular cov o dispersion de 12 samples (?)

# Not urgent
# TODO: ordenar README_develop seccion "headband en estado normal"
# IDEA: expandir muse module para que chequee estado bateria y reciba aceletrometro, etc

def normalize_time(timestamps):
    """Receive a list of np arrays of timestamps. Return the concatenated and normalized (substract initial time) np array"""

    # Concat y normalizar timestamps
    timestamps = np.concatenate(timestamps)
    return timestamps - timestamps[0]

def normalize_data(data):
    """Return the data concatenated"""
    return np.concatenate(data, 1).T

def save_csv(data, timestamps, fname, subfolder=None):
    """Preprocess the data and save it to a csv """
    # Concatenar data
    data = normalize_data(data)

    # Juntar en dataframe
    res = pd.DataFrame(data=data, columns=['TP9', 'AF7', 'AF8', 'TP10', 'Right AUX'])
    res['timestamps'] = timestamps

    # Guardar a csv
    save_data(res, fname, subfolder)

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
    group_save.add_argument('-o', '--only_stream', action="store_true",
                        help="Save only the data that is streamed")


    group_sconn = parser.add_argument_group(title="Stream connection", description=None)
    group_sconn.add_argument('--ip', default="localhost", type=str,
                        help="Host ip to do the streaming")
    group_sconn.add_argument('--port', default=8889, type=int,
                        help="Port to send the data to")
    group_sconn.add_argument('--url', default="/data/muse", type=str,
                        help="Path in the client to send the data, so it will be sent to 'http://ip:port/url'")


    return parser

def main():
    """Connect with muse and stream the data"""
    # Parse args
    parser = create_parser()
    args = parser.parse_args()

    # Argumentos
    args.url = basic.assure_startswith(args.url, "/")
    notify = False
    if notify:
        msg = "You choose to stream the data in the '{}' mode".format(args.stream_mode)
        if args.stream_mode == "n":
            msg += ", with n = {}".format(args.stream_n)
        print(msg)

    ##### Queues para stream datos, thread safe
    # Productor: muse
    # Consumidor: flask, que manda datos a client
    msize = 10 # maxsize
    q_data = deque(maxlen=msize)
    q_time = deque(maxlen=msize)
    lock_queues = threading.Lock()

    ##### Listas para guardar datos
    full_time = []
    full_data = []

    def process_muse_data(data, timestamps):
        """Stores and enqueues the incoming muse data

        - data comes in ndarrays of 5x12, 5 channels and 12 samples
        - timestamps comes in ndarrays of 12x1, 12 samples"""

        # Agregar a full lists
        full_time.append(timestamps)
        full_data.append(data)

        # Agregar datos a queue
        with lock_queues:
            q_time.append(timestamps)
            q_data.append(data)

    # Conectar muse
    muse = Muse(args.address, process_muse_data, interface=args.interface,
        norm_factor=args.nfactor, norm_sub=args.nsub) # factores para normalizar
    status = muse.connect()
    if status != 0:
        basic.perror("Can't connect to muse band", exit_code=status)



    # Generador para streaming
    app = Flask(__name__) # iniciar app de Flask
    CORS(app) # para que cliente pueda acceder a este puerto
    @app.route(args.url)
    def stream_data():
        """ """

        # String para hacer yield
        yield_string = "data: {}, {}, {}, {}, {}, {}\n\n"
            # Siempre se envia (timestamp, ch0, ch1, ch2, ch3, ch4)

        def get_data_mean(tt, t_init, data, dummy=None):
            """Yield the mean in the 12 samples for each channel separately"""
            yield yield_string.format( \
                    tt.mean() - t_init, \
                    data[0].mean(), \
                    data[1].mean(), \
                    data[2].mean(), \
                    data[3].mean(), \
                    data[4].mean() )

        def get_data_max(tt, t_init, data, dummy=None):
            """Yield the max of the 12 samples for each channel separately"""
            # NOTE: use tt.max(), tt.mean()?
            yield yield_string.format( \
                    tt.max() - t_init, \
                    data[0].max(), \
                    data[1].max(), \
                    data[2].max(), \
                    data[3].max(), \
                    data[4].max() )

        def get_data_min(tt, t_init, data, dummy=None):
            """Yield the min of the 12 samples for each channel separately"""
            yield yield_string.format( \
                    tt.min() - t_init, \
                    data[0].min(), \
                    data[1].min(), \
                    data[2].min(), \
                    data[3].min(), \
                    data[4].min() )

        def get_data_n(tt, t_init, data, n):
            """Yield n out of the 12  """
            for i in range(n):
                ttt = tt[i] - t_init
                yield yield_string.format(
                    ttt, \
                    data[0][i], \
                    data[1][i], \
                    data[2][i], \
                    data[3][i], \
                    data[4][i] )

        # Escoger yielder
        yielders = {
            "mean": get_data_mean,
            "min": get_data_min,
            "max": get_data_max,
            "n": get_data_n
            }

        try:
            get_data = yielders[args.stream_mode]
        except:
            basic.perror("yielder: {} not found".format(args.stream_mode), force_continue=True)
            get_data = get_data_n

        # Cap the amount of data to yield
        if args.stream_n > 12:
            args.stream_n = 12
        elif args.stream_n <= 0:
            args.stream_n = 1

        n_data = args.stream_n # Usado para hacer yield de cierta cantidad de datos del total
        drop_full = args.save and args.only_stream

        def event_stream():
            # DEBUG:
            t_act = 0
            t_old = 0
            dt = 1 # print cada 1 seg

            if drop_full: # Al iniciar la conexion, borrar lo anterior
                full_time = []
                full_data = []

            # Drop old data
            with lock_queues:
                q_time.clear()
                q_data.clear()
                t_init = time() # Set an initial time as marker

            # Stream
            while True:
                # sleep(0.1)
                lock_queues.acquire()
                if(len(q_time) == 0 or len(q_data) == 0): # NOTE: ambas length debiesen ser iguales siempre
                    # No data, continue
                    lock_queues.release()
                    continue

                # Tomar dato que viene
                t = q_time.popleft()
                d = q_data.popleft()
                lock_queues.release()

                # NOTE: if len(t) != 12 or d.shape != (5, 12) : may be an index exception
                yield from get_data(t, t_init, d, n_data)

                # DEBUG printing time:
                # t_act = t[-1]
                # if(t_act - t_old >= dt): # 1 second passed
                #     print(t_act)
                #     t_old = t_act

        return Response(event_stream(), mimetype="text/event-stream")

    # Thread para streaming
    stream = threading.Thread(target=app.run, kwargs={"host":args.ip, "port":args.port})
    stream.daemon = True




    # Capturar ctrl-c
    catcher = basic.SignalCatcher()
    signal.signal(signal.SIGINT, catcher.signal_handler)

    ## Iniciar
    muse.start()
    stream.start()

    print("Started receiving muse data...")
    if args.time is None:
        while catcher.keep_running():
            sleep(1)
    else:
        print("\tfor (aprox) {} seconds".format(args.time)) # HACK
        sleep(args.time)

    muse.stop()
    muse.disconnect()
    print("Stopped receiving muse data")


    ##### Guardar todo
    full_time = normalize_time(full_time)

    print("Received data for {:.2f} seconds".format(full_time[-1]))

    if args.save:
        save_csv(full_data, full_time, args.fname, subfolder=args.subfolder)

    return 0


if __name__ == "__main__":
    main()
