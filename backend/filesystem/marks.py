"""Handle marks files."""
import pandas as pd
from backend import info
from . import base

class MarksFileHandler(base.BaseFileHandler):
    """Handle Marks files."""

    name = "marks"
    main_folder = "marks"
    extension = "csv"

    @classmethod
    def save_data(cls, filename, timestamps, messages):
        """Save marks (timestamps and messages) as csv"""
        if len(timestamps) == 0 or len(messages) == 0: # No marks provided
            return False

        df = pd.DataFrame()
        df[info.times_column] = timestamps
        df[info.messages_column] = messages
        df.to_csv(filename)

        return True

    @classmethod
    def load_data(cls, filename):
        """Read a marks file."""
        df = pd.read_csv(filename)
        timestamps = list(df[info.times_column])
        messages = list(df[info.messages_column])

        return timestamps, messages
