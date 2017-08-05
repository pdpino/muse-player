#!/usr/bin/env python
"""Play muse data

Connects with a muse (2016) device, stream the data through a text/event-stream and save the data to a csv"""

from time import sleep, time
import pandas as pd
import argparse
import threading
from flask import Response, Flask   # Stream data to client
from flask_cors import CORS
from muse import Muse
import basic
import backend as b

def parse_args():
    """Create a parser, get the args, return them preprocessed."""
    def create_parser():
        """ Create the console arguments parser"""
        parser = argparse.ArgumentParser(description='Send muse data to client and save to .csv',
                            usage='%(prog)s [options]', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        parser.add_argument('--stream_other', action="store_true",
                            help="DEBUG option, stream other channels")
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
                            help="Choose what part of the data to yield to the client. If 'n' is selected consider providing a --stream_n argument as well")
        group_data.add_argument('--stream_n', default=1, type=int,
                            help="If --stream_mode n is selected, define the amount of data to yield")
        group_data.add_argument('--nsub', default=None, type=int,
                            help="Normalize substractor. Number to substract to the raw data when incoming, before the factor. If None, it will use the muse module default value")
        group_data.add_argument('--nfactor', default=None, type=int,
                            help="Normalize factor. Number to multiply the raw data when incoming. If None, it will use the muse module default value")


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
    eeg_buffer = b.EEGBuffer(name="eeg", yield_function=b.EEGYielder.get_yielder(args.stream_mode))
    data_buffer = b.DataBuffer(name="other", yield_function=b.DataYielder.get_data)

    # Conectar muse
    muse = Muse(args.address, eeg_buffer.incoming_data, data_buffer.incoming_data, norm_factor=args.nfactor, norm_sub=args.nsub)
    muse.connect(interface=args.interface)

    # Init Flask
    app = Flask(__name__) # iniciar app de Flask
    CORS(app) # para que cliente pueda acceder a este puerto
    stream = threading.Thread(target=app.run, kwargs={"host":args.ip, "port":args.port})
    stream.daemon = True

    # Catch ctrl-c
    # catcher = basic.SignalCatcher()

    # Connect data to send
    if not args.stream_other: # Connect EEGdata
        @app.route(args.url)
        def stream_eeg():
            """Stream the eeg data."""
            return Response(eeg_buffer.data_generator(args.stream_n), mimetype="text/event-stream")
    else: # Connect Other data # DEPRECATED: delete this
        basic.perror("Streaming other data is deprecated", force_continue=True)
        @app.route(args.url)
        def stream_other():
            """Stream other data."""
            return Response(data_buffer.data_generator(), mimetype="text/event-stream")

    ## Iniciar
    muse.start()
    stream.start()

    # To save marks in time
    marks = []
    messages = []

    print("Started receiving data")
    if args.time is None:
        # while catcher.keep_running():
        #     sleep(1)

        # HACK: use this in SignalCatcher, or make a permanent solution (that can be used when fixing time to listen)
        try:
            while True:
                message = input("Mark (optional message): ")
                # Mark time
                t = eeg_buffer.get_last_timestamp()
                marks.append(t)
                messages.append(message)
        except: # Ctrl-c
            print("You pressed ctrl c")
            catcher = basic.SignalCatcher() # Add a catcher so you don't press ctrl-c twice

    else:
        print("\tfor (aprox) {} seconds".format(args.time)) # HACK
        sleep(args.time)


    muse.stop()
    muse.disconnect()
    print("Stopped receiving muse data")

    # Imprimir mensajes que recibio Muse en todo el proceso
    # muse.print_msgs()

    # # DEBUG: save a file with the handles
    # df = pd.DataFrame(muse.lista)
    #
    # col0 = df.columns[0]
    # df[col0] = df[col0] - df[col0][0] # Normalizar tiempo
    # df.to_csv("debug/debug2.csv", index=False, header=False) # Guardar a archivo



    # Print running time
    print("\tReceived data for {}".format(eeg_buffer.get_running_time()))


    if args.save:
        eeg_buffer.save_csv(args.fname, subfolder=args.subfolder)
        marks = eeg_buffer.normalize_marks(marks)
        b.data.save_marks(marks, messages, args.fname, subfolder=args.subfolder)

    return 0


if __name__ == "__main__":
    main()
