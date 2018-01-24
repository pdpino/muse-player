""" ."""
import matplotlib.pyplot as plt
from .base import *

def plot_eeg(timestamps, df, channels=None, fname="", marks_t=None, marks_m=None, subplots=False, title="Raw eeg"):
    """Plot raw channels."""

    if channels is None:
        channels = list(df.columns)

    i = 1
    for channel in channels:
        if subplots:
            plt.subplot(4, 1, i) # HACK: hardcoded for 4 channels
            i += 1
        plt.plot(timestamps, df[channel].as_matrix(), label=channel)

        if subplots: # OPTIMIZE
            plot_marks(marks_t, marks_m)

        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')

    if not subplots:
        plot_marks(marks_t, marks_m, show_legend=False)
        plt.legend()

    if not fname is None:
        title += "from {}".format(fname)

    plt.suptitle(title, fontsize=20)
    plot_show()
    plt.show()
