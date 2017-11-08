"""Common functions for the plots submodule."""
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from backend import info
import basic

def plot_show(maximize=True):
    """Wrapper to show the plot by maximizing the window size."""
    # Maximize window
    if maximize:
        mng = plt.get_current_fig_manager()
        # mng.frame.Maximize(True) # 'wx' backend
        # mng.window.showMaximized() # 'Qt4Agg' backend
        mng.resize(*mng.window.maxsize()) # 'TkAgg' backend
        # mng.full_screen_toggle() # Screen to full (really full) size (can't even see the exit button)

    plt.show()

def plot_marks(marks_t, marks_m, ignore_calibration=False, alternate_colors=False, alternate_lines=False):
    """Plot marks in time."""
    if marks_t is None or marks_m is None:
        return

    if len(marks_t) != len(marks_m):
        basic.perror("Marks times and messages do not match", force_continue=True)
        return

    # NOTE: to use a scale of colors:
    # colors = 'winter' #'BuGn'
    # cm = plt.get_cmap(colors)
    # n = len(marks_t)
    # # Then use color=cm(i/n)

    def choose_same_or_alternate(options, alternate=True):
        """Return a lambda function that return options[0] all the time or cylce through options, depending on same"""
        if alternate:
            return lambda i: options[i % len(options)]
        else:
            return lambda i: options[0]

    get_color = choose_same_or_alternate(['black', 'blue'], alternate_colors)
    get_linestyle = choose_same_or_alternate(['-', '--', ':'], alternate_lines)

    i_color = 0
    for i in range(len(marks_t)):
        mark_time = marks_t[i]
        mark_label = marks_m[i]

        i_color += 1

        if info.is_stop_mark(mark_label):
            mark_label = None # No label
            i_color -= 1

        if ignore_calibration and info.is_calib_mark(mark_label):
            mark_label = None

        color = get_color(i_color)
        linestyle = get_linestyle(i_color)

        plt.axvline(mark_time, linestyle=linestyle, color=color, label=mark_label)

    plt.legend(loc='upper center')

def plot_histogram(wave, dist_fn=None, dist_args=None, title=None):
    """Plot an histogram of the data, plus an adjusted distribution if provided."""

    # is in REFACTOR process
    return

    plt.hist(wave, normed=True)

    if not dist_fn is None and not dist_args is None:
        # X axis for the distribution
        t = np.linspace(*plt.xlim(), 100)
        d = dist_fn(t, *dist_args)
        plt.plot(t, d)

    plt.title(title)
    plot_show()
    plt.show()
