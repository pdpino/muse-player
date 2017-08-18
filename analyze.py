#/usr/bin/env python
"""Script to analyze the raw eeg data"""

import argparse
import pandas as pd
import numpy as np
from backend import data, tf, plots, parsers, info, signals
import basic

def calc_tf_analysis(times, df, channels, fname, method, fsave=None, marks_t=None, marks_m=None, testing=False, filtering=False, normalize=True, baseline=None, overwrite=True, window=None, step=None, n_cycles=None):
    """Calculate TF analysis and save to file.

    times -- seconds array
    df -- dataframe with the raw data
    channels -- name of the chosen channels. Each must have a column in the dataframe
    fname -- name of the run used
    method -- must be one of 'stfft' or 'conv'
    marks_t -- list of times of the marks
    marks_m -- list of messages of the marks
    testing -- boolean indicating if testing
    filtering -- boolean
    normalize -- boolean indicating if TF normalization with baseline should be done
    baseline -- list or tuple of two elements, indicating the starting and ending seconds to select as baseline. If None, it will be searched in the marks. If no baseline found in the marks, no baseline normalization can be performed
    overwrite -- boolean indicating if the saved file must be overwritten
    window -- integer parameter passed to stfft
    step -- integer parameter passed to stfft
    n_cycles -- integer parameter passed to convolution"""

    def find_baseline(marks_times, marks_messages):
        """Find baseline marks."""
        if marks_times is None or marks_messages is None:
            return None

        # Name of the marks of calibration
        start = info.start_calib_mark
        stop = info.stop_calib_mark

        if start in marks_messages and stop in marks_messages:
            i1 = marks_messages.index(start)
            i2 = marks_messages.index(stop)

            return [marks_times[i1], marks_times[i2]]
        else:
            return None

    # To choose method # REVIEW: move this to backend?
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

    # Find baseline
    if baseline is None:
        baseline = find_baseline(marks_t, marks_m)
        if not baseline is None:
            basic.report("Found a baseline in the marks")
        else:
            basic.report("No baseline found")

    # Name to save
    fsave = fsave or fname

    for ch in channels:
        if not testing and not overwrite:
            if data.exist_waves(fsave, ch):
                continue

        # Grab data
        eeg_data = df[ch].as_matrix()

        # Apply filters
        if filtering:
            eeg_data = signals.filter_notch(eeg_data)
            # eeg_data = signals.filter_highpass(eeg_data) # FIXME

        # Compute FT
        power = method_function(times, eeg_data, baseline=baseline, norm=normalize, **method_kwargs)

        # Save to file
        data.save_waves(power, fsave, ch)

def show_tf_analysis(channels, fname, marks_t=None, marks_m=None, testing=False, show_contour=False, show_waves=False, show_marks_waves=False, choose_waves=None, n_samples=None, min_freq=None, max_freq=None):
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
    if not testing:
        channels = info.get_chs_plot(channels)

    # Save all powers
    powers = []

    for ch in channels:
        if not data.exist_waves(fname, ch):
            basic.perror("No waves file found for: {}, {}".format(fname, ch), force_continue=True)
            continue
        power = data.load_waves(fname, ch)
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
        plots.plot_marks_waves(mw, channels, fname, choose_waves=choose_waves)

def create_sine_wave(time, srate, freqs, amps, phases):
    """Create a sine wave."""
    # REVIEW: move to backend?

    # Time
    t = np.linspace(0, time, srate*time)
    n_points = len(t)

    # Function to create wave
    new_sine_wave = lambda f, a, ph: np.sin(2*np.pi*f*t + ph)*a

    # Empty sine wave
    sine_wave = np.zeros(n_points)

    # Prepare freq, amp and phase
    def get_value(values, index):
        """ """
        if index >= len(values):
            return values[-1] # by default, return last value
        return values[index]

    # Iterate waves
    n_waves = len(freqs) # Freqs define the amount
    i = 0
    while i < n_waves:
        freq = get_value(freqs, i)
        amp = get_value(amps, i)
        phase = get_value(phases, i)
        sine_wave += new_sine_wave(freq, amp, phase)

        i += 1

    return t, sine_wave

def parse_args():
    """Create parser, parse args, format them and return."""
    def create_parser():
        """Create the console arguments parser."""
        parser = argparse.ArgumentParser(description='Analyze the collected eeg data in the Time-Frequency domain',
                                         usage='%(prog)s [options]')
        subparser = parser.add_subparsers(dest='option')

        #### Calculate parser
        parser_calc = subparser.add_parser('calc')

        # Choose method
        methods = ['stfft', 'conv'] # First is default # REVIEW: move names to backend?
        parser_calc.add_argument('--method', type=str, choices=methods, default=methods[0],
                        help='Method to perform the TF analysis')

        # Other arguments
        parser_calc.add_argument('-t', '--test', action='store_true',
                        help='Test with a simulated wave instead of real data (see testing group)')
        parser_calc.add_argument('-o', '--overwrite', action='store_true', help='Overwrite existing wave data')
        parser_calc.add_argument('--filtering', action='store_true',
                        help='Use a notch filter (50hz) and a high-pass filter (1hz)')

        # Standard arguments
        parsers.add_ch_args(parser_calc)
        parsers.add_file_args(parser_calc, fsave=True)

        # TF arguments
        group_tf = parser_calc.add_argument_group(title="TF general options")
        group_tf.add_argument('--norm', action='store_true', help='If present, normalize the TF')
        group_tf.add_argument('--baseline', nargs=2, help='Range of seconds to normalize the TF')

        # Methods arguments
        group_conv = parser_calc.add_argument_group(title="Morlet wavelet convolution")
        group_conv.add_argument('--cycles', type=int, help='Amount of cycles')

        group_stfft = parser_calc.add_argument_group(title="STFFT")
        group_stfft.add_argument('--window', type=int, help='Window size')
        group_stfft.add_argument('--step', type=int, help='Step to slide the window')

        # Testing
        group_test = parser_calc.add_argument_group(title='Testing',
                                description='Use a sine wave (may be a sum of multiple sine waves) to test the TF analysis')
        group_test.add_argument('--time', type=float, default=1, help='Time to simulate')
        group_test.add_argument('--srate', type=int, default=256, help='Sampling rate')

        group_test.add_argument('--freqs', nargs='+', type=float, default=[10], help='Frequencies')
        group_test.add_argument('--amps', nargs='+', type=float, default=[1], help='Amplitudes')
        group_test.add_argument('--phases', nargs='+', type=float, default=[0], help='Phase angles')





        #### Show parser
        parser_show = subparser.add_parser('show')

        parser_show.add_argument('-t', '--test', action='store_true',
                        help='Test with a simulated wave instead of real data (see testing group)')

        # Hide/show arguments
        parser_show.add_argument('-c', '--show_contour', action='store_true', help='Plot result of convolution and stfft')
        parser_show.add_argument('-w', '--show_waves', action='store_true', help='Plot alpha, beta, etc waves')
        parser_show.add_argument('-m', '--show_marks_waves', action='store_true',
                        help='Plot alpha, beta, etc waves in each mark interval')

        # Standard arguments
        parsers.add_ch_args(parser_show)
        parsers.add_file_args(parser_show)

        # Waves arguments
        group_waves = parser_show.add_argument_group(title="Waves options")
        possible_waves = info.get_waves_names()
        group_waves.add_argument('--waves', nargs='+', choices=possible_waves, default=possible_waves,
                        help='Choose the waves to plot. Only valid for -w and/or -m')
        group_waves.add_argument('--n_samples', type=int,
                        help='In -w option, select a value to plot the waves by groups of n_samples')
        group_waves.add_argument('--range_freq', nargs=2, type=float, help='min and max frequency to plot')

        return parser

    parser = create_parser()
    args = parser.parse_args()

    if args.option == "show":
        if args.range_freq is None:
            args.min_freq = None
            args.max_freq = None
        else:
            args.min_freq, args.max_freq = args.range_freq

        if args.test:
            args.channels = ['sinewave'] # HACK: hardcoded

    return args

if __name__ == "__main__":
    # Parse args
    args = parse_args()


    if args.option == "calc":
        if args.test: # Use simulated data
            # Simulate sine wave
            times, wave = create_sine_wave(args.time, args.srate, args.freqs, args.amps, args.phases)

            # Prepare format (pd.DataFrame)
            sine_name = 'sinewave'
            channels = [sine_name]
            df = pd.DataFrame(columns=channels)
            df[sine_name] = wave

            # No marks
            marks_time = None
            marks_msg = None
        else: # read real data
            # Read dataframe and channels
            times, df, channels = data.load_eeg(args.channels, args.fname, args.subfolder)

            if not args.fsave is None: # HACK copy marks file
                data.copy_marks(args.fname, args.fsave)

            # Read marks in time
            marks_time, marks_msg = data.load_marks(args.fname, args.subfolder)

        # Analyze
        calc_tf_analysis(times, df, channels, args.fname, args.method,
                fsave=args.fsave,
                marks_t=marks_time, marks_m=marks_msg,
                testing=args.test,
                filtering=args.filtering,
                overwrite=args.overwrite,
                normalize=args.norm,
                baseline=args.baseline,
                window=args.window,
                step=args.step,
                n_cycles=args.cycles)

    elif args.option == "show":
        # Read marks in time
        marks_time, marks_msg = data.load_marks(args.fname, args.subfolder)

        # Plot
        show_tf_analysis(args.channels, args.fname,
                marks_t=marks_time, marks_m=marks_msg,
                testing=args.test,
                show_contour=args.show_contour, show_waves=args.show_waves, show_marks_waves=args.show_marks_waves,
                choose_waves=args.waves, n_samples=args.n_samples,
                min_freq=args.min_freq,
                max_freq=args.max_freq)
