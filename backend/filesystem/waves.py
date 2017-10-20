"""Handle wave files."""
import os
import pandas as pd
import basic
from . import filehandler as fh

def load_waves(name, channel, subfolder=None):
    """Read a waves file."""
    fname = fh.DumpFileHandler.get_fname(name, subfolder, suffix=channel, tipo=fh.FileType.waves)

    try:
        df = pd.read_csv(fname, index_col=0)

        basic.report("Waves loaded from file: {}".format(fname))
        return df
    except FileNotFoundError:
        basic.perror("Can't find waves file: {}".format(fname))

def save_waves(power, name, channel, subfolder=None):
    """Save waves to a file."""
    fh.DumpFileHandler.assure_folder(subfolder, fh.FileType.waves)
    fname = fh.DumpFileHandler.get_fname(name, subfolder, suffix=channel, tipo=fh.FileType.waves)

    power.to_csv(fname)
    basic.report("Waves saved to file: {}".format(fname))

def exist_waves(name, channel, subfolder=None):
    """Boolean indicating if waves file exists."""
    return os.path.isfile(fh.DumpFileHandler.get_fname(name, subfolder, suffix=channel, tipo=fh.FileType.waves))
