"""Handle tf files."""
import pandas as pd
from . import base

class TFFiles(base.BaseFileHandler):
    """Handle TimeFrequencyAnalysis (TF) files."""

    name = "TF-analysis"
    folder = "tf"
    extension = "csv"

    @classmethod
    def get_fname(cls, filename, channel, **fname_kwargs):
        return super().get_fname(filename, subfolder, suffix=channel, ext=cls.extension)

    @classmethod
    def save_data(cls, filename, power_df):
        """Save a tf file."""
        power.to_csv(filename)

    @classmethod
    def load_data(cls, filename):
        """Read the TF-power-dataframe from csv."""
        return pd.read_csv(fname, index_col=0)
