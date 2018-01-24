"""Common functions for the plots submodule."""
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from backend import basic, info
from .base import *

def _plot_tsplot(times, arr, n_samples, wave_name):
    """Make a tsplot (see seaborn tsplot).

    Receive an array of a time series, it is reshaped to fit (n_samples, new_time)
    TODO: explain"""

    # Take lengths
    n_array = len(arr) # len of the array
    n_cluster = n_array // n_samples # amount of clusters
    n_array = n_cluster * n_samples # Parse n_array to a divisible number

    # Slice the array
    arr = arr[:n_array]

    # Reshape it
    new_arr = np.reshape(arr, (n_cluster, n_samples))
    new_arr = new_arr.T

    # Reshape times
    times = times[:n_array:n_samples]

    # Make the plot
    sns.tsplot(new_arr, time=times, ci="sd", label=wave_name, color=info.get_wave_color(wave_name))
    # FIXME: add different colors for each wave (hopefully the same color each time)

    # Notes on seaborn.tsplot
    # NOTE: seaborn.tsplot() is deprecated, will be removed or replaced in a future release

    # NOTE: a line in seaborn library needs to be changed in order to pass the label like that:
    # File: "env_muse/lib/python3.5/site-packages/seaborn/timeseries.py", line 351, in tsplot
    # Code: ax.plot(x, central_data, color=color, label=label, **kwargs)
    # Remove label=label argument
    # (because in kwargs there is already a label argument, the one provided here)
    # (is a hack, could be done better)

def plot_waves(waves, ch, fname, marks_t=None, marks_m=None, choose_waves=None, n_samples=None):
    """Receive a list of waves (pd.DataFrame), one for each channel."""

    if n_samples is None:
        plot_function = lambda times, wave, wave_name: plt.plot(times, wave, color=info.get_wave_color(wave_name), label=wave_name)
    else:
        plot_function = lambda times, wave, wave_name: _plot_tsplot(times, wave, n_samples, wave_name)

    def _do_plot_waves(waves, ch_name, marks_t, marks_m):
        """Receive a dataframe of waves and plots them."""
        times = list(waves.index)
        for wave_name in waves.columns:
            if not choose_waves is None:
                if not wave_name in choose_waves: # Skip wave
                    continue
            wave = waves[wave_name].as_matrix()
            plot_function(times, wave, wave_name)

        plot_marks(marks_t, marks_m)

        plt.xlabel('Time (s)')
        plt.ylabel('Power')

        plt.title(ch_name)
        plt.legend()

    if type(waves) is list:
        if len(waves) > 1:
            for i in range(len(waves)):
                w = waves[i]
                c = ch[i]
                plt.subplot(2, 2, i+1)
                _do_plot_waves(w, c, marks_t, marks_m)
        else:
            _do_plot_waves(waves[0], ch[0], marks_t, marks_m)
    else:
        _do_plot_waves(waves, ch, marks_t, marks_m)

    plt.suptitle("Waves from {}".format(fname), fontsize=20)
    plot_show()

def plot_waves_in_marks(all_waves, channels, fname, choose_waves=None):
    """Plot waves in the marks intervals."""

    n_channels = len(channels)
    if len(all_waves) != n_channels:
        basic.perror("plot_waves_in_marks(), lengths don't match")

    def _plot_5(waves, ch):
        """Plot the five waves."""

        messages = waves[info.messages_column]
        messages_index = range(len(messages))

        def _plot_1(w):
            """Plot one wave."""
            wave = waves[w].as_matrix()

            # plt.errorbar(messages_index, wave, yerr=0.1, label=w)
            plt.plot(messages_index, wave, label=w) #, color=info.get_wave_color(w))
            plt.xticks(messages_index, messages, rotation='vertical')

        # Plot all waves
        for w in info.get_waves_names(choose_waves):
            _plot_1(w)

        plt.legend()
        plt.title(ch)
        plt.xlabel('Marks')
        plt.ylabel('Power (dB)')

    if n_channels > 1:
        for i in range(n_channels):
            plt.subplot(2, 2, i+1) # HACK: hardcoded for 4 channels
            _plot_5(all_waves[i], channels[i])
    else:
        _plot_5(all_waves[0], channels[0])

    plt.suptitle("Waves in the marks interval, from {}".format(fname), fontsize=20)

    plot_show()
