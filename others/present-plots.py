#!/usr/bin/env python3
"""Plot specific plots for meetup-visualization presentation (30 Jan 2018)"""
import numpy as np
import matplotlib.pyplot as plt
import argparse
from backend import filesystem as fs

def create_sine_wave(time, srate, freqs, amps, phases):
    """Create a sine wave."""
    # HACK: copied from analyze.py

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
        parser = argparse.ArgumentParser(description='Plot graphs for the presentation', usage='%(prog)s [options]')

        parser.add_argument('--lw', type=float, default=1, help='Linewidth')
        parser.add_argument('--color', type=str, default="r", help='Color')

        parser.add_argument('--time', type=float, default=1, help='Time to simulate')
        parser.add_argument('--srate', type=int, default=256, help='Sampling rate')

        parser.add_argument('--freqs', nargs='+', type=float, default=[10], help='Frequencies')
        parser.add_argument('--amps', nargs='+', type=float, default=[1], help='Amplitudes')
        parser.add_argument('--phases', nargs='+', type=float, default=[0], help='Phase angles')

        return parser

    parser = create_parser()
    args = parser.parse_args()

    return args

def plot_sine_waves(args):
    times, wave = create_sine_wave(args.time, args.srate, args.freqs, args.amps, args.phases)

    plt.plot(times, wave, args.color, lw=args.lw)
    plt.ylim(-2, 2)
    plt.show()

def plot_bars(args):
    powers = np.array(args.amps)**2
    plt.bar(args.freqs, powers)
    plt.xlim(0, 15)
    plt.ylim(0, 1)
    plt.xlabel("Frecuencia (Hz)")
    plt.ylabel("Potencia")
    plt.show()

def plot_freqs(args):
    df = fs.load_tf("miguel_5s_2", channel="AF7")

    arr_freqs = np.array(list(map(float, list(df.columns))))
    values = np.array(list(map(abs, df.iloc[4])))

    plt.bar(arr_freqs, values)
    plt.xlabel("Frecuencia (Hz)")
    plt.ylabel("Potencia (dB)")
    plt.xlim(1, 40)
    plt.show()

def plot_power_law():
    """Plot power law plot. Power vs frequency."""
    k = 3
    a = 700

    t = np.linspace(4, 40, 100)
    p = a*pow(t, -k)

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    _ = plt.plot(t, p)

    for f in [4, 8, 13, 30]:
        plt.axvline(x=f, color='black', linestyle='dotted')

    ax.set_yscale('log')

    plt.ylabel('Log power')
    plt.xlabel('Frequency (Hz)')

    plt.show()

if __name__ == '__main__':
    args = parse_args()

    # plot_sine_waves(args)
    plot_bars(args)
    # plot_freqs(args)
