""" ."""
import numpy as np
import matplotlib.pyplot as plt
from backend import basic, info
from .base import *

def plot_tf_contour(powers, ch, fname="", marks_t=None, marks_m=None, min_freq=None, max_freq=None, maximize=True):
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

        cbar = plt.colorbar(ax)
        cbar.ax.set_ylabel('Power (dB)')

        plt.xlabel('Time (s)')
        plt.ylabel('Frequency (Hz)')


        # Add marks in time
        plot_marks(marks_t, marks_m, ignore_calibration=True, alternate_lines=True)

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
    plot_show(maximize)
