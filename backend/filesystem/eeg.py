"""Handle raw eeg files."""
import pandas as pd
from backend import info
from . import util, base

class EEGFiles(base.BaseFileHandler):
    """Handle EEG files."""

    name = "eeg"
    folder = "eeg"
    extension = "csv"

    @classmethod
    def save_data(cls, filename, eeg_df):
        """Save an eeg dataframe to a .csv"""
        # TODO: Check that the first column is csv
        eeg_df.to_csv(filename, float_format='%f')

    @classmethod
    def load_data(cls, filename):
        """Read the eeg from csv, assure the channels and return the dataframe"""
        df = pd.read_csv(fname, index_col=0)

        if channels is None:
            # Get all channels
            channels = info.get_chs_muse(aux=False)

        # Assure channels in columns
        channels = util._compare_channels(df.columns, channels)
        times = df[info.colname_timestamps]
        df = df[channels]

        return times, df, channels
