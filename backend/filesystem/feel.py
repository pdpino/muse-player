"""Handle feeling files."""
import pandas as pd
from backend import info
import basic

def load_feelings(name, subfolder=None, suffix=None):
    """Read feelings data from csv, assure the channels and return the dataframe"""
    fname = DumpFileHandler.get_fname(name, subfolder, suffix, tipo=FileType.feelings)

    try:
        df = pd.read_csv(fname, index_col=0)
        basic.report("Feelings loaded from file: {}".format(fname))
    except FileNotFoundError:
        basic.perror("The file {} wasn't found".format(fname))

    # Assure channels in columns
    channels = info.get_feelings_colnames()
    channels = _cmp_chs(df.columns, channels)
    times = df[info.colname_timestamps]
    df = df[channels]

    return times, df

def save_feelings(df, name, subfolder=None, suffix=None):
    """Save a feelings dataframe to a .csv"""
    if df is None:
        return

    DumpFileHandler.assure_folder(subfolder, FileType.feelings)
    fname = DumpFileHandler.get_fname(name, subfolder, suffix, tipo=FileType.feelings)

    df.to_csv(fname, float_format='%f')
    basic.report("Feelings saved to file: {}".format(fname))
