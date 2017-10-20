"""Handle raw eeg files."""
import pandas as pd
from backend import info
import basic
from . import filehandler as fh, util

def load_eeg(channels, name, subfolder=None, suffix=None):
    """Read the data from csv, assure the channels and return the dataframe"""
    fname = fh.DumpFileHandler.get_fname(name, subfolder, suffix, tipo=fh.FileType.raw)

    try:
        df = pd.read_csv(fname, index_col=0)
        basic.report("EEG loaded from file: {}".format(fname))
    except FileNotFoundError:
        basic.perror("The file {} wasn't found".format(fname))

    if channels is None:
        # Get all channels
        channels = info.get_chs_muse(aux=False)

    # Assure channels in columns
    channels = util._cmp_chs(df.columns, channels)
    times = df[info.colname_timestamps]
    df = df[channels]

    return times, df, channels

def save_eeg(df, name, subfolder=None, suffix=None):
    """Save a dataframe to a .csv"""
    fh.DumpFileHandler.assure_folder(subfolder, fh.FileType.raw)
    fname = fh.DumpFileHandler.get_fname(name, subfolder, suffix, tipo=fh.FileType.raw)

    # TODO: revisar que la primera columna sea timestamps
    df.to_csv(fname, float_format='%f')
    basic.report("EEG saved to file: {}".format(fname))
