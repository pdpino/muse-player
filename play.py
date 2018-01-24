#!/usr/bin/env python
"""Play muse data

Connects with a muse (2016) device, stream the data to a web client and save the data to a csv"""

import argparse
from backend import parsers, info
from backend.player import MusePlayer

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

        group_muse = parser.add_argument_group(title="Muse connection")
        group_muse.add_argument('--control', action="store_true",
                            help="If present, enable control messages")

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

        group_eeg_data = parser.add_argument_group(title="EEG streamed data", description="Only useful with '--stream eeg' (which is the default)")
        group_eeg_data.add_argument('--eeg_mode', choices=["mean", "n", "max", "min"], type=str, default="n",
                            help="Choose what part of the data to yield to the client. If 'n' is selected consider providing a --eeg_n argument as well")
        group_eeg_data.add_argument('--eeg_n', default=1, type=int,
                            help="If --eeg_mode n is selected, define the amount of data to yield")

        group_waves_data = parser.add_argument_group(title="Waves streamed data", description="Only useful with '--stream waves'")
        group_waves_data.add_argument('--waves', choices=info.get_waves_names(), type=str, nargs="+",
                            help="Select waves to stream")

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
    prefix = "/"
    if not args.url.startswith(prefix):
        args.url = prefix + args.url

    # Cap the amount of data to yield
    if args.eeg_n > 12:
        args.eeg_n = 12
    elif args.eeg_n <= 0:
        args.eeg_n = 1

    return args

def main():
    """Connect with muse and stream the data"""
    args = parse_args()

    player = MusePlayer()

    player.initialize_command_handler()
    player.initialize_eeg_engine(args.stream, args.regulator,
        eeg_mode=args.eeg_mode,
        eeg_n=args.eeg_n,
        waves_selected=args.waves,
        accum_samples=args.accum_samples)
    player.initialize_acc_engine()
    player.initialize_muse(args.address, args.interface, args.faker, nfactor=args.nfactor, nsub=args.nsub, enable_control=args.control)
    player.initialize_flask(args.ip, args.port, args.url)

    player.start(args.time)

    # # DEBUG: save a file with the handles (debugging muse bluetooth)
    # df = pd.DataFrame(muse.lista)
    #
    # col0 = df.columns[0]
    # df[col0] = df[col0] - df[col0][0] # Normalizar tiempo
    # df.to_csv("debug/debug2.csv", index=False, header=False) # Guardar a archivo

    if args.save:
        player.save(args.fname, args.subfolder)

    return 0

if __name__ == "__main__":
    main()
