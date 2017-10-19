"""Handle wave files."""
import os
import pandas as pd
import basic

def load_waves(name, channel, subfolder=None):
    """Read a waves file."""
    fname = DumpFileHandler.get_fname(name, subfolder, suffix=channel, tipo=FileType.waves)

    try:
        df = pd.read_csv(fname, index_col=0)

        basic.report("Waves loaded from file: {}".format(fname))
        return df
    except FileNotFoundError:
        basic.perror("Can't find waves file: {}".format(fname))

def save_waves(power, name, channel, subfolder=None):
    """Save waves to a file."""
    DumpFileHandler.assure_folder(subfolder, FileType.waves)
    fname = DumpFileHandler.get_fname(name, subfolder, suffix=channel, tipo=FileType.waves)

    power.to_csv(fname)
    basic.report("Waves saved to file: {}".format(fname))

def exist_waves(name, channel, subfolder=None):
    """Boolean indicating if waves file exists."""
    return os.path.isfile(DumpFileHandler.get_fname(name, subfolder, suffix=channel, tipo=FileType.waves))
