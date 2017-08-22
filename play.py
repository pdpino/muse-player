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
from backend import parsers, data, engine, info

def parse_args():
    """Create a parser, get the args, return them preprocessed."""
    def create_parser():
        """Create the console arguments parser."""
        parser = argparse.ArgumentParser(description='Send muse data to client and save to .csv',
                            usage='%(prog)s [options]',
                            formatter_class=argparse.ArgumentDefaultsHelpFormatter) # To show default values

        parser.add_argument('-t', '--time', default=None, type=float,
                            help="Seconds to record data (aprox). If none, stop listening only when interrupted")
        parser.add_argument('--save', action="store_true", help="Save a .csv with the raw data")
        parser.add_argument('--stream', action="store_true", help="Stream the data to a web client")
        parser.add_argument('-w', '--stream_waves', action="store_true",
                            help="Stream the wave data (instead of EEG) (beta)")


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
    if args.stream_waves:
        data_buffer = engine.WaveBuffer(name="waves", window=256, step=25, srate=256)
    else:
        data_buffer = engine.EEGBuffer(name="eeg",
                            yield_function=engine.EEGYielder.get_yielder(args.stream_mode))

    # Conectar muse
    muse = Muse(address=args.address,
                callback=data_buffer.incoming_data,
                # callback_other=other_buffer.incoming_data, # DEBUG: see other data
                push_info=True, # DEBUG: push info msgs from muse (to ask config, see battery percentage)
                norm_factor=args.nfactor, norm_sub=args.nsub)
    muse.connect(interface=args.interface)

    # Init Flask
    if args.stream:
        basic.report("Streaming enabled", level=0)

        # Flask app
        app = Flask(__name__) # iniciar app de Flask
        CORS(app) # para que cliente pueda acceder a este puerto

        # Thread
        stream = threading.Thread(target=app.run, kwargs={"host":args.ip, "port":args.port})
        stream.daemon = True

        # Set args for the generator
        if args.stream_waves:
            gen_args = [] # No arguments
        else:
            gen_args = [args.stream_n]

        # Connect data to send
        @app.route(args.url)
        def stream_data():
            """Stream the eeg data."""
            return Response(data_buffer.data_generator(*gen_args), mimetype="text/event-stream")

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

        def ask_config():
            muse.ask_config() # only works if push_info was enabled
            sleep(0.5) # let it print
            return None
        def start_calib():
            if not data_buffer.start_calibrating(): # Indicate if success
                return None
            print("started calibrating")
            return info.start_calib_mark
        def stop_calib():
            if not data_buffer.stop_calibrating():
                return None
            print("stopped calibrating")
            return info.stop_calib_mark
        def start_collect():
            if not data_buffer.start_collecting(): # Indicate if success
                return None
            print("started collecting")
            return info.start_collect_mark
        def stop_collect():
            if not data_buffer.stop_collecting():
                return None
            print("stopped collecting")
            return info.stop_collect_mark
        def toggle_save_opt():
            args.save = not args.save
            print("save status = {}".format(args.save))
            return None

        commands = {
            "-c": ask_config, # DEBUG: you can input this to see what comes in config in muse
            "-1": start_calib,
            "-2": stop_calib,
            "-3": start_collect,
            "-4": stop_collect,
            "--save": toggle_save_opt
            }

        try:
            basic.report("Input (special commands start with '-'; any other string mark the time with a message; ctrl-c to exit):", level=0)
            while True:
                # Mark time
                message = input("\tcmd: ")
                t = data_buffer.get_last_timestamp()

                # Special commands
                if message in commands:
                    message = commands[message]()
                    if message is None:
                        continue

                # Save
                marks.append(t)
                messages.append(message.lower())
        except KeyboardInterrupt: # Ctrl-c
            print("Exiting")
            basic.mute_ctrlc() # So the finishing process isn't interrupted
    else:
        basic.mute_ctrlc()
        basic.report("for (aprox) {} seconds", args.time, level=1)
        sleep(args.time) # HACK: its aprox time

    print("Stopping muse") # DEBUG
    muse.stop()
    print("Disconnecting muse") # DEBUG
    muse.disconnect()
    basic.report("Stopped receiving muse data", level=0)
    print("muse out") # DEBUG

    # # DEBUG: save a file with the handles
    # df = pd.DataFrame(muse.lista)
    #
    # col0 = df.columns[0]
    # df[col0] = df[col0] - df[col0][0] # Normalizar tiempo
    # df.to_csv("debug/debug2.csv", index=False, header=False) # Guardar a archivo

    # Print running time
    basic.report("Received data for {}", data_buffer.get_running_time(), level=1)

    if args.save:
        data_buffer.save_csv(args.fname, subfolder=args.subfolder)
        marks = data_buffer.normalize_marks(marks)
        data.save_marks(marks, messages, args.fname, subfolder=args.subfolder)

    return 0


if __name__ == "__main__":
    main()
