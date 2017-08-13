#/usr/bin/env python
"""Script to analyze the raw eeg data"""

import argparse
import pandas as pd
import numpy as np
from backend import data, tf, plots, parsers
import basic

def tf_analysis(times, df, channels, method, testing,
                name, # Name of the run
                normalize=True,
                baseline=None,
                overwrite=True, # Override an existing waves file
                show_contour=False, show_waves=False, show_marks_waves=False, # Hide/show options
                choose_waves=None, # Choose which waves to plot
                marks_t=None, marks_m=None, # Marks in time
                min_freq=None, max_freq=None, # Range of freq
                window=None, step=None, # Parameters to stfft
                n_cycles=None): # parameters to convolute
    """TF analysis."""

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

    # HACK: reorder channels
    if len(channels) == 4: # If they are all of them
        channels = ['TP9', 'TP10', 'AF7', 'AF8']

    # Save all powers
    powers = []

    # Find baseline
    if baseline is None:
        baseline = find_baseline(marks_t, marks_m)
        if not baseline is None:
            basic.report("Found a baseline in the marks")
        else:
            basic.report("No baseline found")

    for ch in channels:
        if not testing and not overwrite:
            if data.exist_waves(name, ch):
                power = data.load_waves(name, ch)
                powers.append(power)
                continue

        # Grab data
        eeg_data = df[ch].as_matrix()

        # Compute FT
        power = method_function(times, eeg_data, baseline=baseline, norm=normalize, **method_kwargs)

        # Save FT
        powers.append(power)

        # Save to file
        if not testing:
            data.save_waves(power, name, ch)

    # Plot as contour
    if show_contour:
        plots.plot_tf_contour(powers, channels,
                        marks_t=marks_t, marks_m=marks_m,
                        min_freq=min_freq, max_freq=max_freq)

    # Get and plot waves
    if show_waves:
        waves = tf.get_waves(powers)
        plots.plot_waves(waves, channels, marks_t=marks_t, marks_m=marks_m, choose_waves=choose_waves)


    # Get and plot waves in intervals
    if show_marks_waves:
        mw = tf.get_marks_waves(powers, marks_t, marks_m)
        plots.plot_marks_waves(mw, channels, choose_waves=choose_waves)

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

def find_baseline(times, marks):
    """Find baseline marks."""
    if times is None or marks is None:
        return None

    # HACK: names hardcoded
    start = "calibrating"
    stop = "stop calibrating"

    if start in marks and stop in marks:
        i1 = marks.index(start)
        i2 = marks.index(stop)

        return [times[i1], times[i2]]
    else:
        return None

def parse_args():
    """Create parser, parse args, format them and return."""
    def create_parser():
        """Create the console arguments parser."""
        parser = argparse.ArgumentParser(description='Analyze the collected eeg data in the Time-Frequency domain',
                                         usage='%(prog)s [options]')

        # Choose method
        methods = ['stfft', 'conv'] # First is default # REVIEW: move names to backend?
        parser.add_argument('--method', type=str, choices=methods, default=methods[0],
                        help='Method to perform the TF analysis')

        # Hide/show arguments
        parser.add_argument('-c', '--show_contour', action='store_true', help='Plot result of convolution and stfft')
        parser.add_argument('-w', '--show_waves', action='store_true', help='Plot alpha, beta, etc waves')
        parser.add_argument('-m', '--show_marks_waves', action='store_true',
                        help='Plot alpha, beta, etc waves in each mark interval')

        possible_waves = ['delta', 'theta', 'alpha', 'beta', 'gamma']
        parser.add_argument('--waves', nargs='+', choices=possible_waves, default=possible_waves,
                        help='Choose the waves to plot. Only valid for -w and/or -m')

        # Other arguments
        parser.add_argument('-t', '--test', action='store_true', help='Test with a simulated wave instead of real data')
        parser.add_argument('-o', '--overwrite', action='store_true', help='Overwrite existing wave data')

        # Channels argument
        parsers.add_ch_args(parser)

        # Methods arguments
        group_tf = parser.add_argument_group(title="TF general options")
        group_tf.add_argument('--norm', action='store_true', help='If present, normalize the TF')
        group_tf.add_argument('--baseline', nargs=2, help='Range of seconds to normalize the TF')
        group_tf.add_argument('--range_freq', nargs=2, type=float, help='min and max frequency to plot')

        # Methods arguments
        group_conv = parser.add_argument_group(title="Morlet wavelet convolution")
        group_conv.add_argument('--cycles', type=int, help='Amount of cycles')

        group_stfft = parser.add_argument_group(title="STFFT")
        group_stfft.add_argument('--window', type=int, help='Window size')
        group_stfft.add_argument('--step', type=int, help='Step to slide the window')

        # File arguments
        parsers.add_file_args(parser)

        # Testing
        group_test = parser.add_argument_group(title='Testing',
                                description='Use a sine wave (may be a sum of others) to test the TF analysis')
        group_test.add_argument('--time', type=float, default=1, help='Time to simulate')
        group_test.add_argument('--srate', type=int, default=256, help='Sampling rate')

        group_test.add_argument('--freqs', nargs='+', type=float, default=[10], help='Frequencies')
        group_test.add_argument('--amps', nargs='+', type=float, default=[1], help='Amplitudes')
        group_test.add_argument('--phases', nargs='+', type=float, default=[0], help='Phase angles')

        return parser

    parser = create_parser()
    args = parser.parse_args()

    if args.range_freq is None:
        args.min_freq = None
        args.max_freq = None
    else:
        args.min_freq, args.max_freq = args.range_freq


    return args

if __name__ == "__main__":
    # Parse args
    args = parse_args()

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

        # Read marks in time
        marks_time, marks_msg = data.load_marks(args.fname, args.subfolder)


    # Analyze
    tf_analysis(times, df, channels, args.method, args.test, args.fname,
            overwrite=args.overwrite,
            normalize=args.norm,
            baseline=args.baseline,
            show_contour=args.show_contour, show_waves=args.show_waves, show_marks_waves=args.show_marks_waves,
            choose_waves=args.waves,
            marks_t=marks_time, marks_m=marks_msg,
            min_freq=args.min_freq,
            max_freq=args.max_freq,
            window=args.window,
            step=args.step,
            n_cycles=args.cycles)
