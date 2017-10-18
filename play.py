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
from backend import parsers, data, engine, info, tf, MuseFaker

def get_regulator(selected, signals):
    # REFACTOR: use better way of passing the configuration
    if selected == "accum":
        regulator = engine.collectors.DataAccumulator(samples=10)
    elif selected == "calib":
        regulator = engine.calibrators.Calibrator(engine.calibrators.BaselineFeeling())
        signals["-1"] = regulator.signal_start_calibrating
        signals["-2"] = regulator.signal_stop_calibrating
    else:
        regulator = None

    return regulator

def parse_args():
    """Create a parser, get the args, return them preprocessed."""
    def create_parser():
        """Create the console arguments parser."""
        parser = argparse.ArgumentParser(description='Send muse data to client and save to .csv',
                            usage='%(prog)s [options]',
                            formatter_class=argparse.ArgumentDefaultsHelpFormatter) # To show default values

        parser.add_argument('-t', '--time', default=None, type=float,
                            help="Seconds to record data (aprox). If none, stop listening only when interrupted")
        parser.add_argument('--faker', action="store_true", help="Simulate a fake muse. Used for testing")
        parser.add_argument('--save', action="store_true", help="Save a .csv with the raw data")
        parser.add_argument('--stream', action="store_true", help="Stream the data to a web client")
        parser.add_argument('--stream_type', choices=['eeg', 'waves', 'feel', 'feel_val_aro'], default='eeg',
                            help="Select what to stream") # TODO: use config dictionaries somewhere else

        parser.add_argument('--regulator', choices=['accum', 'calib'],
                            help="Select the type of regulator to use") # REFACTOR: this shouldnt be here



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

        group_feeling = parser.add_argument_group(title="Feeling calculation")
        group_feeling.add_argument('--test_population', action='store_true',
                            help="If present, use a populations test instead of a simple hypothesis test")
        group_feeling.add_argument('--feel_interval', type=float, default=1,
                            help="Interval in seconds to grab feeling data")


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

    # Dictionary for the signals
    signals = dict()

    # Select processor for the EEG data
    name = args.stream_type
    if args.stream_type == 'eeg':
        # Use a normal buffer
        eeg_buffer = engine.buffers.EEGBuffer()

        # Generator yields raw EEG
        generator = engine.EEGRawYielder(args.stream_mode, args=(args.stream_n,))

    elif args.stream_type == 'waves':
        # Use a window buffer
        eeg_buffer = engine.buffers.EEGWindowBuffer()

        # Create wave yielder
        window = 256 # HACK: values for the yielder hardcoded
        srate = 256
        channel = 0
        arr_freqs = tf.get_freqs_resolution(window, srate)
        wave_yielder = engine.yielders.WaveYielder(arr_freqs, channel=channel)

        # Wave processor that uses the wave yielder
        generator = engine.WaveProcessor(wave_yielder)

    elif args.stream_type == 'feel':
        # Use a window buffer
        eeg_buffer = engine.buffers.EEGWindowBuffer()

        # Create yielder for the feelings
        feeler = engine.feelers.FeelerRelaxConc()

        # Select regulator
        regulator = get_regulator(args.regulator, signals)

        # Feeling processor, that use the feeler and the regulator
        feel_processor = engine.FeelProcessor(feeler, regulator)

        # Wave processor, that uses the feel processor
        generator = engine.WaveProcessor(feel_processor)

    elif args.stream_type == 'feel_val_aro':
        # Use a window buffer
        eeg_buffer = engine.buffers.EEGWindowBuffer()

        # Create feeler
        feeler = engine.feelers.FeelerValAro()

        # Select regulator
        regulator = get_regulator(args.regulator, signals)

        # Feeling processor, that use the feeler and the regulator
        feel_processor = engine.FeelProcessor(feeler, regulator)

        # Wave processor, that uses the feel processor
        generator = engine.WaveProcessor(feel_processor)

    else:
        raise("Stream type not recognized: {}".format(args.stream_type))


    # Engine that handles the incoming, processing and outgoing data
    eeg_engine = engine.EEGEngine(name, eeg_buffer, generator)

    # Connect muse
    if args.faker:
        muse = MuseFaker(callback=eeg_engine.incoming_data)
    else:
        muse = Muse(address=args.address,
                    callback=eeg_engine.incoming_data,
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

        # Connect data to send
        @app.route(args.url)
        def stream_data():
            """Stream the eeg data."""
            return Response(eeg_engine.outgoing_data(), mimetype="text/event-stream")

    ## Iniciar
    muse.start()
    if args.stream:
        stream.start()

    # To save marks in time
    marks = []
    messages = []

    print("Started receiving data")
    if args.time is None:
        # Wait for a buffer zone
        sleep(1)

        def ask_config():
            muse.ask_config() # only works if push_info was enabled
            sleep(0.5) # let it print

        def toggle_save_opt():
            args.save = not args.save
            print("save status = {}".format(args.save))


        signals["-c"] = ask_config # DEBUG: you can input this to see what comes in config in muse
        signals["--save"] = toggle_save_opt

        try:
            print("Input (special commands start with '-'; any other string mark the time with a message; ctrl-c to exit):")
            while True:
                # Mark time
                message = input("\tcmd: ")
                timestamp = eeg_engine.get_last_timestamp()

                # Special commands
                if message in signals:
                    signals[message]()
                    continue

                # Save
                marks.append(timestamp)
                messages.append(message.lower())
        except KeyboardInterrupt: # Ctrl-c
            print("Exiting")
            basic.mute_ctrlc() # So the finishing process isn't interrupted
    else:
        basic.mute_ctrlc()
        print("\tfor (aprox) {} seconds".format(args.time))
        sleep(args.time) # HACK: its aprox time

    muse.stop()
    # print("Muse stopped") # DEBUG
    muse.disconnect() # FIXME: sometimes a thread gets stuck here
    # print("Muse disconnected") # DEBUG

    print("Stopped receiving muse data")

    # # DEBUG: save a file with the handles (debugging muse bluetooth)
    # df = pd.DataFrame(muse.lista)
    #
    # col0 = df.columns[0]
    # df[col0] = df[col0] - df[col0][0] # Normalizar tiempo
    # df.to_csv("debug/debug2.csv", index=False, header=False) # Guardar a archivo

    # Print running time
    basic.report("Received data for {}", eeg_engine.get_running_time(), level=1)

    if args.save:
        # Save eeg data
        eeg = eeg_engine.export()
        data.save_eeg(eeg, args.fname, args.subfolder)

        ## Save marks
        # marks = data_buffer.normalize_marks(marks)
        # data.save_marks(marks, messages, args.fname, subfolder=args.subfolder)
        #
        # # Save feelings, if any
        # if type(data_buffer) is engine.WaveBuffer:
        #     feelings = data_buffer.get_feelings()
        #     data.save_feelings(feelings, args.fname, args.subfolder)

    return 0


if __name__ == "__main__":
    main()
