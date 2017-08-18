"""Module that provide functions to plot eeg data."""
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from backend import info
import basic

def _maximize():
    """Maximize the window."""
    # Maximize window
    mng = plt.get_current_fig_manager()
    # mng.frame.Maximize(True) # 'wx' backend
    # mng.window.showMaximized() # 'Qt4Agg' backend
    mng.resize(*mng.window.maxsize()) # 'TkAgg' backend
    # mng.full_screen_toggle() # Screen to full (really full) size (can't even see the exit button)

def _plot_marks(marks_t, marks_m):
    """Plot marks in time."""
    if marks_t is None or marks_m is None:
        return

    if len(marks_t) != len(marks_m):
        basic.perror("Marks times and messages do not match", force_continue=True)
    else:
        # NOTE: to use a scale of colors:
        # colors = 'winter' #'BuGn'
        # cm = plt.get_cmap(colors)
        # n = len(marks_t)
        # # Then use color=cm(i/n)

        for i in range(len(marks_t)):
            t = marks_t[i]
            m = marks_m[i]
            if info.is_stop_mark(m):
                m = None # No label
            plt.axvline(t, color='black', label=m)
        plt.legend(loc='upper center')

def plot_tf_contour(powers, ch, fname, marks_t=None, marks_m=None, min_freq=None, max_freq=None):
    """Plot a contour plot with the power.

    powers -- list of dataframes, one per channel; columns are frequencies, index are times
    ch -- name of the channel(s)
    fname -- filename, added to the title
    marks_t -- time marks
    marks_m -- messages of the marks
    min_freq -- minimum frequency to the plot
    max_freq -- maximum frequency to the plot

    """

    def _plot_1(power, channel, marks_t, marks_m, min_freq, max_freq):
        """Plot a power contour."""
        # Set DEFAULTs # 4, 50 is decent
        if min_freq is None:
            min_freq = 0
        if max_freq is None:
            max_freq = 100

        # Select frequencies
        arr_freqs = info.filter_freqs(power.columns, min_freq, max_freq)
        power = power[arr_freqs]

        arr_times = np.array(power.index)
        matrix = power.as_matrix()
        matrix = np.transpose(matrix) # fix axis

        # Plot
        colors = 'nipy_spectral' #'bwr'  #'seismic' #'coolwarm' #
        ax = plt.contourf(arr_times, arr_freqs, matrix, 50, cmap=plt.get_cmap(colors))
        plt.colorbar(ax)
        plt.xlabel('Time (s)')
        plt.ylabel('Frequency (Hz)')


        # Add marks in time
        _plot_marks(marks_t, marks_m)

        plt.title(channel)


    args = [marks_t, marks_m, min_freq, max_freq]

    if len(powers) == 0:
        basic.perror("There is no data to plot in plot_tf_contour")
    elif len(powers) > 1:
        for i in range(len(powers)):
            plt.subplot(2, 2, i+1) # HACK: hardcoded for 4 channels
            _plot_1(powers[i], ch[i], *args)
    else:
        _plot_1(powers[0], ch[0], *args)

    # Superior title
    plt.suptitle("TF analysis from {}".format(fname))

    # Show
    _maximize()
    plt.show()

def plot_eeg(t, df, ch_names, fname, marks_t=None, marks_m=None, subplots=False):
    """Plot raw channels."""

    i = 1
    for ch in ch_names:
        if subplots:
            plt.subplot(2, 2, i) # HACK: hardcoded for 4 channels
            i += 1
        plt.plot(t, df[ch].as_matrix(), label=ch)

        if subplots: # OPTIMIZE
            _plot_marks(marks_t, marks_m)

        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')

    if not subplots:
        _plot_marks(marks_t, marks_m)

    plt.suptitle("Raw eeg from {}".format(fname), fontsize=20)
    plt.legend()
    _maximize()
    plt.show()

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

        _plot_marks(marks_t, marks_m)

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
    _maximize()
    plt.show()

def plot_marks_waves(all_waves, channels, fname, choose_waves=None):
    """Plot waves in the marks intervals."""

    n_channels = len(channels)
    if len(all_waves) != n_channels:
        basic.perror("plot_marks_waves(), lengths don't match")

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

    _maximize()
    plt.show()


def plot_histogram(wave, dist_fn=None, dist_args=None, title=None):
    """Plot an histogram of the data, plus an adjusted distribution if provided."""

    plt.hist(wave, normed=True)

    if not dist_fn is None and not dist_args is None:
        # X axis for the distribution
        t = np.linspace(*plt.xlim(), 100)
        d = dist_fn(t, *dist_args)
        plt.plot(t, d)

    plt.title(title)
    _maximize()
    plt.show()
