#/usr/bin/env python
"""Plot different kinds of saved data."""
import argparse
from backend import filesystem, plots, parsers, info, tf

def show_tf_analysis(channels, fname, marks_t=None, marks_m=None, show_contour=False, show_waves=False, show_marks_waves=False, choose_waves=None, n_samples=None, min_freq=None, max_freq=None):
    """Show TF analysis loaded from file.

    channels -- name of the chosen channels. Each must have a column in the dataframe
    fname -- name of the run used
    marks_t -- list of times of the marks
    marks_m -- list of messages of the marks
    show_contour -- boolean indicating if plot the contour
    show_waves -- boolean indicating if plot the waves
    show_marks_waves -- boolean indicating if plot the waves averaged between marks
    choose_waves -- list of waves chosen
    n_samples -- parameter passed to the tsplot
    min_freq -- minimum frequency to plot in the contour plot
    max_freq -- maximum frequency to plot in the contour plot"""

    # Order channels in plot order
    channels = info.get_chs_plot(channels)

    # Save all powers
    powers = []

    for ch in channels:
        if not filesystem.exist_tf(fname, ch):
            basic.perror("No waves file found for: {}, {}".format(fname, ch), force_continue=True)
            continue
        power = filesystem.load_tf(fname, ch)
        powers.append(power)

    if len(powers) == 0:
        basic.perror("No wave to show")

    # Plot as contour
    if show_contour:
        plots.plot_tf_contour(powers, channels, fname,
                        marks_t=marks_t, marks_m=marks_m,
                        min_freq=min_freq, max_freq=max_freq)

    # Get and plot waves
    if show_waves:
        waves = tf.get_waves(powers)
        plots.plot_waves(waves, channels, fname, marks_t=marks_t, marks_m=marks_m,
                        choose_waves=choose_waves, n_samples=n_samples)

    # Get and plot waves in intervals
    if show_marks_waves:
        mw = tf.get_marks_waves(powers, marks_t, marks_m)
        plots.plot_waves_in_marks(mw, channels, fname, choose_waves=choose_waves)

def parse_args():
    """Parse console arguments."""

    def create_parser():
        parser = argparse.ArgumentParser(description='Plot different kinds of data', usage='%(prog)s [options]')

        subparsers = parser.add_subparsers(dest='option')

        parser_eeg = subparsers.add_parser('eeg')
        parser_eeg.add_argument('--subplot', action='store_true', help='Plot each channel in a subplot')
        parsers.add_ch_args(parser_eeg)
        parsers.add_file_args(parser_eeg)

        parser_tf = subparsers.add_parser('tf')
        parser_tf.add_argument('--lines', action='store_true', help='Plot with lines instead of dots')
        parsers.add_ch_args(parser_tf)
        parsers.add_file_args(parser_tf)

        group_waves = parser_tf.add_argument_group(title="Waves options")
        possible_waves = info.get_waves_names()
        group_waves.add_argument('--waves', nargs='+', choices=possible_waves, default=possible_waves,
                        help='Choose the waves to plot. Only valid for -w and/or -m')
        group_waves.add_argument('--n_samples', type=int,
                        help='In -w option, select a value to plot the waves by groups of n_samples')
        group_waves.add_argument('--range_freq', nargs=2, type=float, help='min and max frequency to plot')


        parser_tf.add_argument('-c', '--show_contour', action='store_true', help='Plot result of convolution and stfft')
        parser_tf.add_argument('-w', '--show_waves', action='store_true', help='Plot alpha, beta, etc waves')
        parser_tf.add_argument('-m', '--show_marks_waves', action='store_true',
                        help='Plot alpha, beta, etc waves in each mark interval')


        parser_feelings = subparsers.add_parser('feel')
        parser_feelings.add_argument('--lines', action='store_true', help='Plot with lines instead of dots')
        parsers.add_file_args(parser_feelings)

        return parser

    parser = create_parser()
    args = parser.parse_args()

    if args.option == 'tf':
        # REFACTOR
        if args.range_freq is None:
            args.min_freq = None
            args.max_freq = None
        else:
            args.min_freq, args.max_freq = args.range_freq

    return args

if __name__ == "__main__":
    args = parse_args()

    # Read marks in time
    marks_time, marks_msg = filesystem.load_marks(args.fname, args.subfolder)

    if args.option == 'eeg':
        times, df, channels = filesystem.load_eeg(args.channels, args.fname, args.subfolder)
        plots.plot_eeg(times, df, channels, args.fname, marks_t=marks_time, marks_m=marks_msg, subplots=args.subplot)
    elif args.option == 'tf':
        show_tf_analysis(args.channels, args.fname,
                marks_t=marks_time, marks_m=marks_msg,
                show_contour=args.show_contour, show_waves=args.show_waves, show_marks_waves=args.show_marks_waves,
                choose_waves=args.waves, n_samples=args.n_samples,
                min_freq=args.min_freq,
                max_freq=args.max_freq)
    elif args.option == 'feel':
        times, df = filesystem.load_feelings(args.fname, args.subfolder)
        plots.plot_feelings(times, df, args.fname, marks_t=marks_time, marks_m=marks_msg, lines=args.lines)
