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
from backend import parsers, filesystem, engine, info, tf, MuseFaker
from player import CommandHandler

def get_regulator(selected, commands, accum_samples=10):
    # REFACTOR: use better way of passing the configuration
    if selected == "accum":
        regulator = engine.collectors.DataAccumulator(samples=accum_samples)
    elif selected == "calib":
        regulator = engine.calibrators.Calibrator(engine.calibrators.BaselineFeeling())
        commands.add_command("-3", regulator.signal_start_calibrating, info.start_collect_mark, 'notification')
        commands.add_command("-4", regulator.signal_stop_calibrating, info.stop_collect_mark, 'notification')
    else:
        regulator = None

    return regulator

def set_signal_commands_generator(generator, commands):
    # REFACTOR this
    commands.add_command("-1", generator.signal_start_calibrating, info.start_calib_mark, "notification")
    commands.add_command("-2", generator.signal_stop_calibrating, info.stop_calib_mark, "notification")

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
        parser.add_argument('--save', action="store_true", help="Save a .csv with the raw eeg data")

        parser.add_argument('--stream', nargs='?', choices=['eeg', 'waves', 'feel', 'feel_val_aro'], const='eeg', help="Stream data to a client") # REFACTOR: use config dictionaries somewhere else

        # REFACTOR: this shouldnt be here
        parser.add_argument('--regulator', choices=['accum', 'calib'],
                            help="Select the type of regulator to use")
        parser.add_argument('--accum_samples', type=int, default=10,
                            help="Choose amount of samples to accumulate")

        group_bconn = parser.add_argument_group(title="Bluetooth connection")
        group_bconn.add_argument('-i', '--interface', default=None, type=str,
                            help="Bluetooth interface, e.g: hci0, hci1")
        group_bconn.add_argument('-a', '--address', default="00:55:DA:B3:20:D7", type=str,
                            help="Device's MAC address")

        group_sconn = parser.add_argument_group(title="Stream connection", description=None)
        group_sconn.add_argument('--ip', default="localhost", type=str,
                            help="Host ip to do the streaming")
        group_sconn.add_argument('--port', default=8001, type=int,
                            help="Port to send the data to")
        group_sconn.add_argument('--url', default="/stream", type=str,
                            help="Path in the client to send the data, so it will be sent to 'http://ip:port/url'")

        group_proc_data = parser.add_argument_group(title="Processed Data")
        group_proc_data.add_argument('--nsub', default=None, type=int,
                            help="Normalize substractor. Number to substract to the raw data when incoming, before the factor. If None, it will use the muse module default value")
        group_proc_data.add_argument('--nfactor', default=None, type=int,
                            help="Normalize factor. Number to multiply the raw data when incoming. If None, it will use the muse module default value")

        group_stream_data = parser.add_argument_group(title="Streamed Data", description="Only useful when streaming eeg")
        group_stream_data.add_argument('--stream_mode', choices=["mean", "n", "max", "min"], type=str, default="n",
                            help="Choose what part of the data to yield to the client. If 'n' is selected consider providing a --stream_n argument as well")
        group_stream_data.add_argument('--stream_n', default=1, type=int,
                            help="If --stream_mode n is selected, define the amount of data to yield")

        # group_feeling = parser.add_argument_group(title="Feeling calculation")
        # group_feeling.add_argument('--test_population', action='store_true',
        #                     help="If present, use a populations test instead of a simple hypothesis test")
        # group_feeling.add_argument('--feel_interval', type=float, default=1,
        #                     help="Interval in seconds to grab feeling data")

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

    # Dictionary for the commands
    commands = CommandHandler()

    # Select processor for the EEG data
    stream_enabled = not args.stream is None
    if args.stream == 'eeg':
        # Use a normal buffer
        eeg_buffer = engine.buffers.EEGBuffer()

        # Generator yields raw EEG
        generator = engine.EEGRawYielder(args.stream_mode, stream_n=args.stream_n)

    elif args.stream == 'waves':
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
        set_signal_commands_generator(generator, commands)

    elif args.stream == 'feel':
        # Use a window buffer
        eeg_buffer = engine.buffers.EEGWindowBuffer()

        # Create yielder for the feelings
        feeler = engine.feelers.FeelerRelaxConc()

        # Select regulator
        regulator = get_regulator(args.regulator, commands, args.accum_samples)

        # Feeling processor, that use the feeler and the regulator
        feel_processor = engine.FeelProcessor(feeler, regulator,
            [info.colname_relaxation, info.colname_concentration])

        # Wave processor, that uses the feel processor
        generator = engine.WaveProcessor(feel_processor)
        set_signal_commands_generator(generator, commands)

    elif args.stream == 'feel_val_aro':
        # Use a window buffer
        eeg_buffer = engine.buffers.EEGWindowBuffer()

        # Create feeler
        feeler = engine.feelers.FeelerValAro()

        # Select regulator
        regulator = get_regulator(args.regulator, commands, args.accum_samples)

        # Feeling processor, that use the feeler and the regulator
        feel_processor = engine.FeelProcessor(feeler, regulator,
            [info.colname_arousal, info.colname_valence])

        # Wave processor, that uses the feel processor
        generator = engine.WaveProcessor(feel_processor)
        set_signal_commands_generator(generator, commands)

    elif args.stream is None:
        eeg_buffer = engine.buffers.EEGBuffer()

        generator = engine.EEGRawYielder(args.stream_mode, stream_n=args.stream_n)
    else:
        basic.perror("Stream type not recognized: {}".format(args.stream))

    # Engine that handles the incoming, processing and outgoing data
    eeg_collector = engine.collectors.EEGCollector()
    eeg_engine = engine.EEGEngine(args.stream, eeg_collector, eeg_buffer, generator)

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
    if stream_enabled:
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
    if stream_enabled:
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
            print("\tsave status = {}".format(args.save))

        commands.add_command("-c", ask_config, None, None)
        commands.add_command("--save", toggle_save_opt, None, None)

        try:
            while True:
                # Mark time
                message = input("cmd: ")
                timestamp = eeg_collector.get_last_timestamp()

                # Special commands
                if commands.exist_command(message):
                    message = commands.apply_command(message)
                    if message is None:
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
    muse.disconnect() # FIXME: sometimes a thread gets stuck here

    print("Stopped receiving muse data")

    # # DEBUG: save a file with the handles (debugging muse bluetooth)
    # df = pd.DataFrame(muse.lista)
    #
    # col0 = df.columns[0]
    # df[col0] = df[col0] - df[col0][0] # Normalizar tiempo
    # df.to_csv("debug/debug2.csv", index=False, header=False) # Guardar a archivo

    # Print running time
    basic.report("Received data for {}", eeg_collector.get_running_time(), level=1)

    if args.save:
        # Save eeg data
        eeg = eeg_collector.export()
        filesystem.save_eeg(args.fname, eeg, folder=args.subfolder)

        # Save marks
        marks = eeg_collector.normalize_marks(marks)
        filesystem.save_marks(args.fname, marks, messages, folder=args.subfolder)

        # Save feelings, if any
        try: # HACK: use something more elegant than try catch
            feelings = feel_processor.export()
            if not feelings is None:
                filesystem.save_feelings(args.fname, feelings, folder=args.subfolder)
        except UnboundLocalError as e:
            pass

    return 0


if __name__ == "__main__":
    main()
