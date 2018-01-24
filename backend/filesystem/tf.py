"""Handle tf files."""
import pandas as pd
from . import base

class TFFileHandler(base.BaseFileHandler):
    """Handle TimeFrequency Analysis (TF) files."""

    name = "TF-analysis"
    main_folder = "tf"
    extension = "csv"

    @classmethod
    def get_fname(cls, name, **kwargs):
        """Override get_fname() to decorate standard behavior"""
        kwargs["suffix"] = kwargs.get("channel")
        return super().get_fname(name, **kwargs)

    @classmethod
    def save_data(cls, filename, power_df):
        """Save a tf file."""
        power_df.to_csv(filename)
        return True

    @classmethod
    def load_data(cls, filename):
        """Read the TF-power-dataframe from csv."""
        return pd.read_csv(filename, index_col=0)
