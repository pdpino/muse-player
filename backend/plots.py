"""Module that provide functions to plot eeg data."""
import numpy as np
import matplotlib.pyplot as plt
# import basic

def plot_tf_contour(power, min_freq=4, max_freq=50, subplot=None, show=True):
    """Plot a contour plot with the power.

    power -- dataframe, columns are frequencies, index are times"""

    # Select frequencies
    arr_freqs = []
    for f in power.columns:
        if min_freq < f and f < max_freq:
            arr_freqs.append(f)
    power = power[arr_freqs]

    arr_times = np.array(power.index)
    matrix = power.as_matrix()
    matrix = np.transpose(matrix) # fix axis

    if not subplot is None:
        plt.subplot(subplot)

    ax = plt.contourf(arr_times, arr_freqs, matrix, 50, cmap=plt.get_cmap('nipy_spectral'))
    plt.colorbar(ax)
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Frequency (Hz)')

    if show:
        plt.show()

def plot_raw(df, ch_names, subplots=False):
    """Plot raw channels."""

    t = df['timestamps'].as_matrix()
    i = 1
    for ch in ch_names:
        if subplots:
            plt.subplot(3, 2, i) # HACK: hardcoded for 6 subplots
            i += 1
        plt.plot(t, df[ch].as_matrix(), label=ch)

    plt.suptitle("Raw channels", fontsize=20)
    plt.legend()
    plt.show()
