#/usr/bin/env python
"""Script to plot the raw eeg data"""

import argparse
from backend import data, plots, parsers

def create_parser():
    """Create the console arguments parser."""

    parser = argparse.ArgumentParser(description='Plot the raw eeg data', usage='%(prog)s [options]')
    parsers.add_ch_args(parser) # Add channel argument
    parser.add_argument('--subplot', action='store_true', help='Plot each channel in a subplot')
    parsers.add_file_args(parser) # Add file arguments

    return parser

if __name__ == "__main__":
    # Parse args
    parser = create_parser()
    args = parser.parse_args()

    # Read dataframe and channels
    times, df, channels = data.load_eeg(args.channels, args.fname, args.subfolder)

    # Read marks in time
    marks_time, marks_msg = data.load_marks(args.fname, args.subfolder)

    # Plot
    plots.plot_eeg(times, df, channels, marks_t=marks_time, marks_m=marks_msg, subplots=args.subplot)
