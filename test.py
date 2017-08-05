#/usr/bin/env python
"""Script to test the TF functions."""
import argparse
from backend import plots, tf

import numpy as np

def test_tf(t, wave, plot_waves=False, hide_result=False, min_freq=None, max_freq=None, window=None, step=None, n_cycles=None):
    """Test TF analysis on a wave."""

    # Compute FT
    power_stfft = tf.stfft(t, wave, norm=False, window=window, step=step)
    power_conv = tf.convolute(t, wave, norm=False, n_cycles=n_cycles)

    ch = "sine wave"
    # Plot as contour
    if not hide_result:
        plots.plot_tf_contour(power_stfft, "STFFT", ch, min_freq=min_freq, max_freq=max_freq, subplot=121, show=False)
        plots.plot_tf_contour(power_conv, "Convolution", ch, min_freq=min_freq, max_freq=max_freq, subplot=122)

    # Get and plot waves
    if plot_waves:
        waves = tf.get_waves(power_conv)
        plots.plot_waves(waves, ch, "Convolution")

def create_sine_wave(time, srate, freqs, amps, phases, plot=False):
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

    if plot:
        plots.plot_channel(t, sine_wave, title="Sine wave, {} Hz, amp={}, phi={}".format(freqs, amps, phases))

    return t, sine_wave

def create_parser():
    """Create the console arguments parser."""
    parser = argparse.ArgumentParser(description='Test the TF functions', usage='%(prog)s [options]')

    parser.add_argument('-s', '--plot_sine', action='store_true', help='Plot the sine wave when created')
    parser.add_argument('-r', '--hide_result', action='store_true', help='Don\'t plot result of convolution and stfft')
    parser.add_argument('-w', '--plot_waves', action='store_true', help='Plot alpha, beta, etc waves')
    # parser.add_argument('--range_freq', nargs=2, type=float, help='min and max frequency to plot')

    group_wave = parser.add_argument_group(title='Sine wave arguments')
    group_wave.add_argument('-t', '--time', type=float, default=1, help='Time to simulate')
    group_wave.add_argument('--srate', type=int, default=256, help='Sampling rate')

    # HACK: hardcoded default values # DEFAULT
    group_wave.add_argument('--freq', nargs='+', type=float, default=[10], help='Frequency')
    group_wave.add_argument('--amp', nargs='+', type=float, default=[1], help='Amplitude')
    group_wave.add_argument('--phase', nargs='+', type=float, default=[0], help='Phase angle')

    group_conv = parser.add_argument_group(title="Morlet wavelet convolution")
    group_conv.add_argument('--cycles', type=int, help='Amount of cycles')

    group_stfft = parser.add_argument_group(title="STFFT")
    group_stfft.add_argument('--window', type=int, help='Window size')
    group_stfft.add_argument('--step', type=int, help='Step to slide the window')

    return parser

if __name__ == "__main__":
    # Parse args
    parser = create_parser()
    args = parser.parse_args()

    # Create wave
    t, wave = create_sine_wave(args.time, args.srate, args.freq, args.amp, args.phase, args.plot_sine)

    # Test wave
    # if args.range_freq is None:
    #     min_freq = None
    #     max_freq = None
    # else:
    #     min_freq, max_freq = args.range_freq


    test_tf(t, wave,
            plot_waves=args.plot_waves,
            hide_result=args.hide_result,
            # min_freq=min_freq,
            # max_freq=max_freq,
            window=args.window,
            step=args.step,
            n_cycles=args.cycles)
