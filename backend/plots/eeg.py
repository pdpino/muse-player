""" ."""
import matplotlib.pyplot as plt
from .base import *

def plot_eeg(t, df, ch_names, fname, marks_t=None, marks_m=None, subplots=False):
    """Plot raw channels."""

    i = 1
    for ch in ch_names:
        if subplots:
            plt.subplot(2, 2, i) # HACK: hardcoded for 4 channels
            i += 1
        plt.plot(t, df[ch].as_matrix(), label=ch)

        if subplots: # OPTIMIZE
            plot_marks(marks_t, marks_m)

        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')

    if not subplots:
        plot_marks(marks_t, marks_m)

    plt.suptitle("Raw eeg from {}".format(fname), fontsize=20)
    plt.legend()
    plot_show()
    plt.show()
