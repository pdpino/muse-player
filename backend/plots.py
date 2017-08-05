"""Module that provide functions to plot eeg data."""
import numpy as np
import matplotlib.pyplot as plt
# import basic

def _plot_marks(marks_t, marks_m):
    """Plot marks in time."""
    if marks_t is None or marks_m is None:
        return

    if len(marks_t) != len(marks_m):
        basic.perror("Marks times and messages do not match", force_continue=True)
    else:
        for i in range(len(marks_t)):
            t = marks_t[i]
            m = marks_m[i]
            plt.axvline(t, color='black', label=m)
        plt.legend()

def plot_tf_contour(power, title, channel, marks_t=None, marks_m=None, min_freq=None, max_freq=None, subplot=None, show=True):
    """Plot a contour plot with the power.

    power -- dataframe, columns are frequencies, index are times
    title -- title to the plot
    channel -- name of the channel is added to the title
    marks_t -- time marks
    marks_m -- messages of the marks
    min_freq -- minimum frequency to the plot
    max_freq -- maximum frequency to the plot
    subplot -- call a subplot
    show -- if present, show the plot when finished
    """

    # Set DEFAULTs # 4, 50 is decent
    if min_freq is None:
        min_freq = 0
    if max_freq is None:
        max_freq = 100

    # Select frequencies
    arr_freqs = []
    for f in power.columns:
        if min_freq < f and f < max_freq:
            arr_freqs.append(f)

    # arr_freqs = list(power.columns) # DEBUG: to force plotting all frequencies
    power = power[arr_freqs]

    arr_times = np.array(power.index)
    matrix = power.as_matrix()
    matrix = np.transpose(matrix) # fix axis

    if not subplot is None:
        plt.subplot(subplot)

    ax = plt.contourf(arr_times, arr_freqs, matrix, 50, cmap=plt.get_cmap('nipy_spectral'))
    plt.colorbar(ax)
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')


    # Add marks in time
    _plot_marks(marks_t, marks_m)


    plt.title("{} from {}".format(title, channel))


    if show:
        # Maximize window
        mng = plt.get_current_fig_manager()
        # mng.frame.Maximize(True) # 'wx' backend
        # mng.window.showMaximized() # 'Qt4Agg' backend
        mng.resize(*mng.window.maxsize()) # 'TkAgg' backend
        # mng.full_screen_toggle() # Screen to full size (cant even see the exit button)

        # Show
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

def plot_raw(df, ch_names, marks_t=None, marks_m=None, subplots=False):
    """Plot raw channels."""

    t = df['timestamps'].as_matrix()
    i = 1
    for ch in ch_names:
        if subplots:
            plt.subplot(3, 2, i) # HACK: hardcoded for 6 subplots
            i += 1
        plt.plot(t, df[ch].as_matrix(), label=ch)
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')

    _plot_marks(marks_t, marks_m)

    plt.suptitle("Raw channels", fontsize=20)
    plt.legend()
    plt.show()

def plot_waves(waves, ch_name, method, marks_t=None, marks_m=None):
    """Receive a list of waves and plots them. waves is a pd.DataFrame"""

    times = list(waves.index)
    for wave_name in waves.columns:
        wave = waves[wave_name].as_matrix()
        plt.plot(times, wave, label=wave_name)

    _plot_marks(marks_t, marks_m)

    plt.xlabel('Time (s)')
    plt.ylabel('Power')

    plt.suptitle("Waves from {}, using {}".format(ch_name, method), fontsize=20)
    plt.legend()
    plt.show()
