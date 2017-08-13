"""Module that provide functions to plot eeg data."""
import numpy as np
import matplotlib.pyplot as plt
# import basic

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
            if m.startswith("stop"): # HACK: 'stop' hardcoded
                m = None # No label
            plt.axvline(t, color='black', label=m)
        plt.legend(loc='upper center')

def plot_tf_contour(power, ch, title, marks_t=None, marks_m=None, min_freq=None, max_freq=None):
    """Plot a contour plot with the power.

    power -- dataframe (or list of), columns are frequencies, index are times
    ch -- name of the channel(s)
    title -- title to the plot
    marks_t -- time marks
    marks_m -- messages of the marks
    min_freq -- minimum frequency to the plot
    max_freq -- maximum frequency to the plot

    if power is a list, ch must be a list of the same len
    """

    def _do_plot(power, channel, marks_t, marks_m, min_freq, max_freq):
        """Plot a power contour."""
        # Set DEFAULTs # 4, 50 is decent
        if min_freq is None:
            min_freq = 0
        if max_freq is None:
            max_freq = 100

        # Select frequencies
        arr_freqs = []
        for f in power.columns:
            try:
                fr = float(f)
            except:
                continue # Discard that frequency

            if min_freq < fr and fr < max_freq:
                arr_freqs.append(f)

        power = power[arr_freqs]

        arr_times = np.array(power.index)
        matrix = power.as_matrix()
        matrix = np.transpose(matrix) # fix axis

        # Plot
        colors = 'bwr'  #'seismic' #'coolwarm' # 'nipy_spectral'
        ax = plt.contourf(arr_times, arr_freqs, matrix, 50, cmap=plt.get_cmap(colors))
        plt.colorbar(ax)
        plt.xlabel('Time (s)')
        plt.ylabel('Frequency (Hz)')


        # Add marks in time
        _plot_marks(marks_t, marks_m)

        # Title with channel
        plt.title(channel)


    args = [marks_t, marks_m, min_freq, max_freq]

    if type(power) is list:
        # NOTE: Assume that ch is also a list
        if len(power) > 1:
            for i in range(len(power)):
                plt.subplot(2, 2, i+1)
                _do_plot(power[i], ch[i], *args)
        else:
            _do_plot(power[0], ch[0], *args)
    else:
        _do_plot(power, ch, *args)


    # Superior title
    plt.suptitle(title)

    # Show
    _maximize()
    plt.show()

def plot_channel(t, arr, title, xlab='Time (s)', ylab='Amplitude'):
    """Plot a channel."""
    # REVIEW: move xlab and ylab to a centralize place?

    plt.plot(t, arr)
    plt.xlabel(xlab) # DEFAULT is time and amplitude
    plt.ylabel(ylab)
    plt.suptitle(title, fontsize=20)
    plt.show()

def plot_multiple(t, arrays, title, labels, xlab='Time (s)', ylab='Amplitude'):
    """Plot multiple channels."""
    # DEBUG function
    i = 0
    for arr in arrays:
        plt.plot(t, arr, label=labels[i])
        i += 1

    plt.xlabel(xlab) # DEFAULT is time and amplitude
    plt.ylabel(ylab)
    plt.suptitle(title, fontsize=20)
    plt.show()

def plot_raw(t, df, ch_names, marks_t=None, marks_m=None, subplots=False):
    """Plot raw channels."""

    # t = t.as_matrix()

    i = 1
    for ch in ch_names:
        if subplots:
            plt.subplot(3, 2, i) # HACK: hardcoded for 6 subplots
            i += 1
        plt.plot(t, df[ch].as_matrix(), label=ch)

        if subplots: # OPTIMIZE
            _plot_marks(marks_t, marks_m)

        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')

    if not subplots:
        _plot_marks(marks_t, marks_m)

    plt.suptitle("Raw channels", fontsize=20)
    plt.legend()
    _maximize()
    plt.show()

def plot_waves(waves, ch, marks_t=None, marks_m=None, choose_waves=None):
    """Receive a list of waves or a list of lists of waves (one for each channel)."""

    def _do_plot_waves(waves, ch_name, marks_t, marks_m):
        """Receive a list of waves and plots them. waves is a pd.DataFrame"""
        times = list(waves.index)
        for wave_name in waves.columns:
            if not choose_waves is None:
                if not wave_name in choose_waves: # Skip wave
                    continue
            wave = waves[wave_name].as_matrix()
            plt.plot(times, wave, label=wave_name)

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

    plt.suptitle("Waves", fontsize=20)
    _maximize()
    plt.show()

def plot_marks_waves(all_waves, channels, choose_waves=None):
    """Plot waves in the marks intervals."""

    n_channels = len(channels)
    if len(all_waves) != n_channels:
        basic.perror("plot_marks_waves(), lengths don't match")

    def _plot_5(waves, ch):
        """Plot the five waves."""

        messages = waves["messages"]
        messages_index = range(len(messages))

        def _plot_1(w):
            """Plot one wave."""
            if not choose_waves is None:
                if not w in choose_waves:
                    return
            wave = waves[w].as_matrix()

            # plt.errorbar(messages_index, wave, yerr=0.1, label=w)
            plt.plot(messages_index, wave, label=w)
            plt.xticks(messages_index, messages, rotation='vertical')


        delta = _plot_1("delta")
        theta = _plot_1("theta")
        alpha = _plot_1("alpha")
        beta = _plot_1("beta")
        gamma = _plot_1("gamma")

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

    plt.suptitle("Waves in the marks interval", fontsize=20)

    _maximize()
    plt.show()
