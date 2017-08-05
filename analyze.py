#/usr/bin/env python
"""Script to analyze the raw eeg data"""

import argparse
from backend import data, tf, plots
import basic

def tf_analysis(df, channels, method, plot_waves=False, hide_result=False, min_freq=None, max_freq=None, window=None, step=None, n_cycles=None):
    """Get and plot the waves."""

    # Grab time
    times = df['timestamps']

    # To choose method
    ft_functions = {'stfft': tf.stfft, 'conv': tf.convolute }
    ft_args = {
        "stfft": {'window': window, 'step': step},
        "conv": {'n_cycles': n_cycles}
        }
    names = {'stfft': "STFFT", 'conv': "Convolution" }

    # Choose method
    method_kwargs = ft_args[method]
    method_name = names[method]
    method_function = ft_functions[method]

    for ch in channels:
        # Grab data
        eeg_data = df[ch].as_matrix()

        # Compute FT
        power = method_function(times, eeg_data, **method_kwargs)

        # Plot as contour
        if not hide_result:
            plots.plot_tf_contour(power, method_name, ch, min_freq=min_freq, max_freq=max_freq) #, subplot=122)

        # Get and plot waves
        if plot_waves:
            waves = tf.get_waves(power)
            plots.plot_waves(waves, ch, method_name)

def load_data(channels, *file_args):
    """Read the data, assure the channels and return it."""
    # REVIEW: move this to backend?

    df = data.load(*file_args)

    if channels is None:
        # Get all channels
        channels = data.ch_names()

    # Assure channel in columns
    for ch in channels:
        if not ch in df.columns:
            basic.perror("The channel '{}' is not in the loaded file".format(ch))
            # TODO: ignore it # Use sets, intersection and difference

    return df, channels

def create_parser():
    """Create the console arguments parser."""

    def add_args(p):
        """Add basic args to a parser."""
        p.add_argument('--channels', choices=data.ch_names(), default=None, nargs='+',
                            help="Channels to analyze")

        group_data = p.add_argument_group(title="File arguments")
        group_data.add_argument('-f', '--fname', default="data", type=str,
                            help="Name of the .csv file to read")
        group_data.add_argument('--subfolder', default=None, type=str,
                            help="Subfolder to read the .csv file")
        group_data.add_argument('--suffix', default=None, type=str,
                            help="Suffix to append to the filename")

    # Parser and subparsers
    parser = argparse.ArgumentParser(description='Analyze the collected eeg data', usage='%(prog)s [options]')
    subparser = parser.add_subparsers(dest='option')
    subparser.required = True

    # Parser to plot raw data
    p1 = subparser.add_parser('raw', help="Analyze the raw data")
    add_args(p1)
    p1.add_argument('--subplot', action='store_true', help='Plot each channel in a subplot')

    # Parser to TF analysis
    p2 = subparser.add_parser('tf', help="Analyze the data in the Time-Frequency domain")

    # Choose method
    methods = ['stfft', 'conv'] # First is default # REVIEW: move to backend?
    p2.add_argument('method', type=str, choices=methods, default=methods[0],
                    help='Method to perform the TF analysis')

    # Main arguments
    parser.add_argument('-r', '--hide_result', action='store_true', help='Don\'t plot result of convolution and stfft')
    parser.add_argument('-w', '--plot_waves', action='store_true', help='Plot alpha, beta, etc waves')
    p2.add_argument('--range_freq', nargs=2, type=float, help='min and max frequency to plot')
    # p2.add_argument('--range_time', nargs=2, type=float, help='min and max time to plot')
    # TODO: que estos args influyan en que se analiza menos frecuencias (en convolution se puede, stfft no)

    # Method arguments
    group_conv = p2.add_argument_group(title="Morlet wavelet convolution")
    group_conv.add_argument('--cycles', type=int, help='Amount of cycles')

    group_stfft = p2.add_argument_group(title="STFFT")
    group_stfft.add_argument('--window', type=int, help='Window size')
    group_stfft.add_argument('--step', type=int, help='Step to slide the window')

    # Basic arguments
    add_args(p2)

    return parser

if __name__ == "__main__":
    # Parse args
    parser = create_parser()
    args = parser.parse_args()

    df, channels = load_data(args.channels, args.fname, args.subfolder, args.suffix)

    if args.option == "raw":
        plots.plot_raw(df, channels, subplots=args.subplot)
    elif args.option == "tf":
        if args.range_freq is None:
            min_freq = None
            max_freq = None
        else:
            min_freq, max_freq = args.range_freq

        # Analyze
        tf_analysis(df, channels, args.method,
                hide_result=args.hide_result,
                plot_waves=args.plot_waves,
                min_freq=min_freq,
                max_freq=max_freq,
                window=args.window,
                step=args.step,
                n_cycles=args.cycles)
