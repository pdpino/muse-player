#/usr/bin/env python
"""Script to analyze the raw eeg data"""

import argparse
from backend import data, tf, plots
import basic

def tf_analysis(df, channel):
    """Get and plot the waves."""

    if not channel in df.columns:
        basic.perror("The channel '{}' is not in the loaded file".format(args.channel))

    # Tomar data
    eeg_data = df[channel].as_matrix()
    times = df['timestamps']

    power_stfft = tf.stfft(times, eeg_data, window=100, step=20)
    power_conv = tf.convolute(times, eeg_data, n_cycles=15)

    freq1 = 8
    freq2 = 30

    plots.plot_tf_contour(power_stfft, min_freq=freq1, max_freq=freq2, subplot=121, show=False)
    plots.plot_tf_contour(power_conv, min_freq=freq1, max_freq=freq2, subplot=122)

def create_parser():
    """Create the console arguments parser."""
    ch_names = ['TP9', 'AF7', 'AF8', 'TP10'] # HACK: leave this in backend

    parser = argparse.ArgumentParser(description='Analyze the collected eeg data domain',
                        usage='%(prog)s [options]')

    parser.add_argument('--raw', action='store_true',
                        help="Plot the raw channels")

    parser.add_argument('--channel', choices=ch_names, default=None, type=str,
                        help="Channel to extract the waves from")

    group_data = parser.add_argument_group(title="File arguments")
    group_data.add_argument('-f', '--fname', default="data", type=str,
                        help="Name of the .csv file to read")
    group_data.add_argument('--subfolder', default=None, type=str,
                        help="Subfolder to read the .csv file")
    group_data.add_argument('--suffix', default=None, type=str,
                        help="Suffix to append to the filename")

    return parser

if __name__ == "__main__":
    # QUESTION: como juntar todos los canales? o usarlos por separado?
    # Al parecer usarlos por separado

    # Parse args
    parser = create_parser()
    args = parser.parse_args()


    # Read the file
    df = data.read_data(args.fname, args.subfolder, args.suffix)

    if args.raw:
        if args.channel is None:
            ch_names = ['TP9', 'AF7', 'AF8', 'TP10'] # HACK: leave this in backend
        else:
            ch_names = [args.channel]


        plots.plot_raw(df, ch_names, subplots=False)
    else:
        if args.channel is None:
            args.channel = 'AF7' # DEFAULT # HACK
        tf_analysis(df, args.channel)
