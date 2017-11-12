"""Handle feeling files."""
import pandas as pd
from backend import info
import basic
from . import filehandler as fh

def load_feelings(name, subfolder=None, suffix=None):
    """Read feelings data from csv, assure the channels and return the dataframe"""

    basic.perror("Load feelings hasn't been correctly updated, you can't load valence arousal files just yet", force_continue=True)

    fname = fh.DumpFileHandler.get_fname(name, subfolder, suffix, tipo=fh.FileType.feelings)

    try:
        df = pd.read_csv(fname, index_col=0)
        basic.report("Feelings loaded from file: {}".format(fname))
    except FileNotFoundError:
        basic.perror("The file {} wasn't found".format(fname))

    # Assure channels in columns
    channels = info.get_feelings_colnames()
    channels = _compare_channels(df.columns, channels)
    times = df[info.colname_timestamps]
    df = df[channels]

    return times, df

def save_feelings(df, name, subfolder=None, suffix=None):
    """Save a feelings dataframe to a .csv"""
    if df is None:
        return

    fh.DumpFileHandler.assure_folder(subfolder, fh.FileType.feelings)
    fname = fh.DumpFileHandler.get_fname(name, subfolder, suffix, tipo=fh.FileType.feelings)

    df.to_csv(fname, float_format='%f')
    basic.report("Feelings saved to file: {}".format(fname))
