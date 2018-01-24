"""Apply ICA and plot topograph maps from data."""
import numpy as np
import pandas as pd
import argparse
import mne
from sklearn.decomposition import FastICA
from backend import filesystem as fs, plots, parsers
import matplotlib.pyplot as plt

def parse_int_range(nums):
    """Parse numbers as a range.

    Example:
    '<3, 45, 48-51, 77' --> [1, 2, 3, 45, 48, 49, 50, 51, 77]
    """
    numbers = []
    for x in map(str.strip,nums.split(',')):
        if x.isdigit():
            numbers.append(int(x))
            continue

        if x[0] == '<':
            numbers.extend(range(1,int(x[1:])+1))
            continue

        if '-' in x:
            xr = map(str.strip,x.split('-'))
            numbers.extend(range(int(xr[0]),int(xr[1])+1))
            continue

    return numbers

def apply_ica(fname, plot_eeg=False, plot_sources=False):
    """Compute and plot ICA from eeg data."""
    # Read eeg data
    timestamps, df, channels = fs.load_eeg(fname)
    marks_timestamps, marks_messages = fs.load_marks(fname)

    # Plot eeg data
    if plot_eeg:
        plots.plot_eeg(timestamps, df, channels, marks_t=marks_timestamps, marks_m=marks_messages,
                fname=fname, subplots=True)

    # Montage of the muse
    montage = mne.channels.read_montage("standard_1020", ch_names=channels)
    info = mne.create_info(channels, sfreq=256, ch_types="eeg", montage=montage)

    # reorder channels
    channels = info["ch_names"]
    df = df[channels]

    # Data as matrix
    eeg = df.as_matrix()

    # Apply FastICA
    fast_ica = FastICA()
    fast_ica.fit(eeg)

    # Plot sources
    sources = fast_ica.transform(eeg)
    if plot_sources:
        df_sources = pd.DataFrame(sources, columns=["s1", "s2", "s3", "s4"])
        plots.plot_eeg(timestamps, df_sources, title="Sources", subplots=True)

    # Mixing matrix
    A = fast_ica.mixing_
    n_channels, n_components = A.shape # 4, 4

    # Plot ica
    fig, axes = plt.subplots(4, 2, gridspec_kw={ "width_ratios": [1, 6] })
    for index in range(4):
        # plot ica
        mne.viz.plot_topomap(A[:, index], pos=info, show=False, axes=axes[index, 0])

        # plot its source right next to it
        plt.sca(axes[index, 1])
        plt.plot(timestamps, sources[:, index])

        plots.base.plot_marks(marks_timestamps, marks_messages, show_legend=False)

    plt.suptitle("Independent Components on {}".format(fname))
    # plt.tight_layout()
    plots.base.plot_show()


    # Delete one component
    delete_ics = parse_int_range(input("Select the component (s) to delete (0-3): "))

    for delete_ic in delete_ics:
        # Override mixing matrix # HACK: is there a better way to do this?
        fast_ica.mixing_[:, delete_ic] = 0

    # Mix sources again
    filtered_eeg = fast_ica.inverse_transform(sources)

    # Remake a df
    filtered_df = pd.DataFrame(filtered_eeg, columns=channels)

    # Plot it
    plots.plot_eeg(timestamps, filtered_df, marks_t=marks_timestamps, marks_m=marks_messages, subplots=True, title="Filtered eeg", fname=fname)




def parse_args():
    parser = argparse.ArgumentParser()

    parsers.add_ch_args(parser)
    parsers.add_file_args(parser)

    parser.add_argument("--plot_eeg", action="store_true", help="Plot the eeg channels")
    parser.add_argument("--plot_sources", action="store_true", help="Plot the sources separately")

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    apply_ica(args.fname, plot_eeg=args.plot_eeg, plot_sources=args.plot_sources)
