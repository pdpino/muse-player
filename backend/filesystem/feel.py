"""Handle feeling files."""
import pandas as pd
from backend import info
from . import base

class FeelFileHandler(base.BaseFileHandler):
    """Handle feeling files."""

    name = "feeling"
    main_folder = "feelings"
    extension = "csv"

    @classmethod
    def save_data(cls, filename, df):
        """Save a feelings dataframe to a .csv"""
        if df is None: # REVIEW: necessary?
            return False

        df.to_csv(filename, float_format='%f')

        return True

    @classmethod
    def load_data(cls, filename):
        """Read the feelings from csv."""

        df = pd.read_csv(filename, index_col=0)
        timestamps = df[info.colname_timestamps]
        df.drop(info.colname_timestamps, axis=1)

        # TODO: assure feelings names??
        # # Assure channels in columns
        # channels = info.get_feelings_colnames()
        # channels = _compare_channels(df.columns, channels)

        return timestamps, df
