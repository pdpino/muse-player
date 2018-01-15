"""Handle raw eeg files."""
import pandas as pd
from backend import info
from . import util, base

class EEGFileHandler(base.BaseFileHandler):
    """Handle EEG files."""

    name = "eeg"
    main_folder = "eeg"
    extension = "csv"

    @classmethod
    def save_data(cls, filename, eeg_df):
        """Save an eeg dataframe to a .csv"""
        # TODO: Check that the first column is csv
        eeg_df.to_csv(filename, float_format='%f')

    @classmethod
    def load_data(cls, filename, channels):
        """Read the eeg from csv, assure the channels and return the dataframe.

        filename -- full filename to load the csv
        channels -- list of channels to load"""
        df = pd.read_csv(filename, index_col=0)

        if channels is None:
            # Get all channels
            channels = info.get_chs_muse(aux=False)

        # Assure channels in columns
        channels = util._compare_channels(df.columns, channels)
        times = df[info.colname_timestamps]
        df = df[channels]

        return times, df, channels
