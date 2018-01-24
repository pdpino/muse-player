""" ."""
import matplotlib.pyplot as plt
from backend import basic, info

def plot_feelings(t, df, fname, marks_t=None, marks_m=None, lines=False):
    """Plot feelings."""

    marker = '-' if lines else 'o'

    for feeling_name in info.get_feelings_colnames():
        if not feeling_name in df.columns:
            basic.perror("{} not found in feelings file".format(feeling_name), force_continue=True)
            continue

        plt.plot(t, df[feeling_name].as_matrix(), marker, label=feeling_name)

        plt.xlabel('Time (s)')
        plt.ylabel('Hypothesis test value')

    plot_marks(marks_t, marks_m, ignore_calibration=True, alternate_colors=False, alternate_lines=True)

    plt.suptitle("Feelings from {}".format(fname), fontsize=20)
    plt.legend()
    plot_show()
