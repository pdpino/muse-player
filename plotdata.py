#/usr/bin/env python
"""Script to plot data."""

import argparse
from backend import data as filesys, plots, parsers

def create_parser():
    """Create the console arguments parser."""

    parser = argparse.ArgumentParser(description='Plot any data', usage='%(prog)s [options]')


    subparsers = parser.add_subparsers(dest='option')

    parser_eeg = subparsers.add_parser('eeg')
    parser_eeg.add_argument('--subplot', action='store_true', help='Plot each channel in a subplot')
    parsers.add_ch_args(parser_eeg)
    parsers.add_file_args(parser_eeg)

    parser_feelings = subparsers.add_parser('feel')
    parser_feelings.add_argument('--lines', action='store_true', help='Plot with lines instead of dots')
    parsers.add_file_args(parser_feelings)

    return parser

if __name__ == "__main__":
    # Parse args
    parser = create_parser()
    args = parser.parse_args()

    # Read marks in time
    marks_time, marks_msg = filesys.load_marks(args.fname, args.subfolder)

    if args.option == 'eeg':
        times, df, channels = filesys.load_eeg(args.channels, args.fname, args.subfolder)
        plots.plot_eeg(times, df, channels, args.fname, marks_t=marks_time, marks_m=marks_msg, subplots=args.subplot)
    elif args.option == 'feel':
        times, df = filesys.load_feelings(args.fname, args.subfolder)
        plots.plot_feelings(times, df, args.fname, marks_t=marks_time, marks_m=marks_msg, lines=args.lines)
