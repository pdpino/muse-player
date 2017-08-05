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
from backend import parsers

def parse_args():
    """Create a parser, get the args, return them preprocessed."""
    def create_parser():
        """Create the console arguments parser."""
        parser = argparse.ArgumentParser(description='Send muse data to client and save to .csv',
                            usage='%(prog)s [options]',
                            formatter_class=argparse.ArgumentDefaultsHelpFormatter) # To show default values

        parser.add_argument('-t', '--time', default=None, type=float,
                            help="Seconds to record data (aprox). If none, stop listening only when interrupted")
        parser.add_argument('-s', '--save', action="store_true", help="Save a .csv with the raw data")
        parser.add_argument('--stream', action="store_true", help="Stream the data to a web client")

        group_bconn = parser.add_argument_group(title="Bluetooth connection")
        group_bconn.add_argument('-i', '--interface', default=None, type=str,
                            help="Bluetooth interface, e.g: hci0, hci1")
        group_bconn.add_argument('-a', '--address', default="00:55:DA:B3:20:D7", type=str,
                            help="Device's MAC address")

        group_sconn = parser.add_argument_group(title="Stream connection", description=None)
        group_sconn.add_argument('--ip', default="localhost", type=str,
                            help="Host ip to do the streaming")
        group_sconn.add_argument('--port', default=8889, type=int,
                            help="Port to send the data to")
        group_sconn.add_argument('--url', default="/data/muse", type=str,
                            help="Path in the client to send the data, so it will be sent to 'http://ip:port/url'")

        group_proc_data = parser.add_argument_group(title="Processed Data")
        group_proc_data.add_argument('--nsub', default=None, type=int,
                            help="Normalize substractor. Number to substract to the raw data when incoming, before the factor. If None, it will use the muse module default value")
        group_proc_data.add_argument('--nfactor', default=None, type=int,
                            help="Normalize factor. Number to multiply the raw data when incoming. If None, it will use the muse module default value")

        group_stream_data = parser.add_argument_group(title="Streamed Data")
        group_stream_data.add_argument('--stream_mode', choices=["mean", "n", "max", "min"], type=str, default="n",
                            help="Choose what part of the data to yield to the client. If 'n' is selected consider providing a --stream_n argument as well")
        group_stream_data.add_argument('--stream_n', default=1, type=int,
                            help="If --stream_mode n is selected, define the amount of data to yield")

        parsers.add_file_args(parser) # File arguments
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
    eeg_buffer = b.EEGBuffer(name="eeg",
                            yield_function=b.EEGYielder.get_yielder(args.stream_mode))

    # Conectar muse
    muse = Muse(address=args.address,
                callback=eeg_buffer.incoming_data,
                # callback_other=data_buffer.incoming_data, # DEBUG: see other data
                push_info=True, # DEBUG: to ask config, see battery percentage
                norm_factor=args.nfactor, norm_sub=args.nsub)
    muse.connect(interface=args.interface)

    # Init Flask
    if args.stream:
        basic.report("Streaming enabled", level=0)
        app = Flask(__name__) # iniciar app de Flask
        CORS(app) # para que cliente pueda acceder a este puerto
        stream = threading.Thread(target=app.run, kwargs={"host":args.ip, "port":args.port})
        stream.daemon = True

        # Connect data to send
        @app.route(args.url)
        def stream_eeg():
            """Stream the eeg data."""
            return Response(eeg_buffer.data_generator(args.stream_n), mimetype="text/event-stream")

    ## Iniciar
    muse.start()
    if args.stream:
        stream.start()

    # To save marks in time
    marks = []
    messages = []

    basic.report("Started receiving data", level=0)
    if args.time is None:
        # Wait for a buffer zone
        sleep(1)

        try:
            while True:
                # Mark time
                message = input("Mark (optional message): ")
                t = eeg_buffer.get_last_timestamp()

                # DEBUG: you can input this to see what comes in config in muse
                if message == "-c": # Magic word
                    muse.ask_config()# only works if push_info was enabled
                    sleep(0.5) # let it print
                    continue

                # Save
                marks.append(t)
                messages.append(message)
        except KeyboardInterrupt: # Ctrl-c
            print("\nYou pressed ctrl c")
            basic.mute_ctrlc() # So the finishing process isn't interrupted
    else:
        basic.mute_ctrlc()
        basic.report("for (aprox) {} seconds", args.time, level=1)
        sleep(args.time) # HACK

    muse.stop()
    muse.disconnect()
    basic.report("Stopped receiving muse data", level=0)

    # # DEBUG: save a file with the handles
    # df = pd.DataFrame(muse.lista)
    #
    # col0 = df.columns[0]
    # df[col0] = df[col0] - df[col0][0] # Normalizar tiempo
    # df.to_csv("debug/debug2.csv", index=False, header=False) # Guardar a archivo



    # Print running time
    basic.report("Received data for {}", eeg_buffer.get_running_time(), level=1)


    if args.save:
        eeg_buffer.save_csv(args.fname, subfolder=args.subfolder)
        marks = eeg_buffer.normalize_marks(marks)
        b.data.save_marks(marks, messages, args.fname, subfolder=args.subfolder)

    return 0


if __name__ == "__main__":
    main()
