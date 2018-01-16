#/usr/bin/env python
"""Script to analyze the raw eeg data"""

import argparse
import pandas as pd
import numpy as np
from backend import basic, filesystem, tf, parsers, info, signals

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

        # OPTIMIZE: use only one query to the list (index != -1, or the like)
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
            print("\tFound a baseline in the marks")
        else:
            print("\tNo baseline found in the marks")

    # Name to save
    fsave = fsave or fname

    for ch in channels:
        if not testing and not overwrite:
            if filesystem.exist_tf(fsave, ch):
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
        filesystem.save_tf(fsave, power, ch)

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

        # Other arguments
        parser.add_argument('-t', '--test', action='store_true',
                        help='Test with a simulated wave instead of real data (see testing group)')
        parser.add_argument('-o', '--overwrite', action='store_true', help='Overwrite existing wave data')
        parser.add_argument('--filtering', action='store_true',
                        help='Use a notch filter (50hz) and a high-pass filter (1hz)')

        # Standard arguments
        parsers.add_ch_args(parser)
        parsers.add_file_args(parser, fsave=True)

        # TF arguments
        group_tf = parser.add_argument_group(title="TF general options")
        methods = ['stfft', 'conv'] # First is default # REVIEW: move names to backend?
        group_tf.add_argument('--method', type=str, choices=methods, default=methods[0],
                        help='Method to perform the TF analysis')
        group_tf.add_argument('--norm', action='store_true', help='If present, normalize the TF')
        group_tf.add_argument('--baseline', nargs=2, help='Range of seconds to normalize the TF')

        # Methods arguments
        group_conv = parser.add_argument_group(title="Morlet wavelet convolution")
        group_conv.add_argument('--cycles', type=int, help='Amount of cycles')

        group_stfft = parser.add_argument_group(title="STFFT")
        group_stfft.add_argument('--window', type=int, help='Window size')
        group_stfft.add_argument('--step', type=int, help='Step to slide the window')

        # Testing
        group_test = parser.add_argument_group(title='Testing',
                                description='Use a sine wave (may be a sum of multiple sine waves) to test the TF analysis')
        group_test.add_argument('--time', type=float, default=1, help='Time to simulate')
        group_test.add_argument('--srate', type=int, default=256, help='Sampling rate')

        group_test.add_argument('--freqs', nargs='+', type=float, default=[10], help='Frequencies')
        group_test.add_argument('--amps', nargs='+', type=float, default=[1], help='Amplitudes')
        group_test.add_argument('--phases', nargs='+', type=float, default=[0], help='Phase angles')

        return parser

    parser = create_parser()
    args = parser.parse_args()

    return args

if __name__ == "__main__":
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
        times, df, channels = filesystem.load_eeg(args.fname, args.channels, folder=args.subfolder)

        if not args.fsave is None: # HACK copy marks file
            filesystem.copy_marks(args.fname, args.fsave)

        # Read marks in time
        marks_time, marks_msg = filesystem.load_marks(args.fname, folder=args.subfolder)

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
