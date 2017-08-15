"""Module that provides functionality to manage the data"""
import os
import pandas as pd
from enum import Enum
from backend import info
import basic

class FileType(Enum):
    raw = 1
    waves = 2
    marks = 3

    def __str__(self):
        if self == FileType.raw:
            return "raw"
        elif self == FileType.waves:
            return "waves"
        elif self == FileType.marks:
            return "marks"
        else:
            return ""

class DumpFileHandler(basic.FileHandler):
    """Handle the dump file and folder names."""

    """Folders."""
    root_folder = "" # HERE
    base_folder = "data"

    """Extension."""
    ext = "csv"

    @classmethod
    def get_subfolder(cls, tipo):
        """Return the folder."""
        return str(tipo)

    @classmethod
    def get_fname(cls, name, subfolder=None, suffix=None, tipo=FileType.raw):
        """Return the vocabulary full filename."""
        subfolder_type = cls.get_subfolder(tipo)
        return cls._get_fname(name, folder=[subfolder_type, subfolder], suffix=suffix, ext=cls.ext)

    @classmethod
    def assure_folder(cls, subfolder, tipo):
        """Assure the existence of a folder."""
        cls._assure_folder(cls.get_subfolder(tipo), subfolder)

def _cmp_chs(real_chs, wanted_chs):
    """Compare the existing channels with the wanted ones, return the intersection and notifies the difference."""
    # Make sets
    real_chs = set(real_chs)
    wanted_chs = set(wanted_chs)

    eff_chs = list(real_chs.intersection(wanted_chs)) # effective channels
    none_chs = list(wanted_chs - real_chs) # non existing channels
    if len(none_chs) > 0:
        basic.perror("The channel '{}' is not in the loaded file".format(ch), force_continue=True)

    return eff_chs

def load_eeg(channels, name, subfolder=None, suffix=None):
    """Read the data from csv, assure the channels and return the dataframe"""
    fname = DumpFileHandler.get_fname(name, subfolder, suffix, tipo=FileType.raw)

    try:
        df = pd.read_csv(fname, index_col=0)
        basic.report("EEG loaded from file: {}".format(fname))
    except FileNotFoundError:
        basic.perror("The file {} wasn't found".format(fname))

    if channels is None:
        # Get all channels
        channels = info.get_chs_muse(aux=False)

    # Assure channels in columns
    channels = _cmp_chs(df.columns, channels)
    times = df[info.timestamps_column]
    df = df[channels]

    return times, df, channels

def save_eeg(df, name, subfolder=None, suffix=None):
    """Save a dataframe to a .csv"""
    DumpFileHandler.assure_folder(subfolder, FileType.raw)
    fname = DumpFileHandler.get_fname(name, subfolder, suffix, tipo=FileType.raw)

    # TODO: revisar que la primera columna sea timestamps
    df.to_csv(fname, float_format='%f')
    basic.report("EEG saved to file: {}".format(fname))

def load_marks(name, subfolder=None):
    """Read a marks file."""
    fname = DumpFileHandler.get_fname(name, subfolder, tipo=FileType.marks)

    try:
        df = pd.read_csv(fname)
        times = list(df[info.times_column])
        messages = list(df[info.messages_column])

        basic.report("Marks loaded from file: {}".format(fname))
        return times, messages
    except FileNotFoundError:
        basic.report("Can't find marks file: {}".format(fname))
        return None, None

def save_marks(times, messages, name, subfolder=None):
    """Save marks to a file."""
    if len(times) == 0 or len(messages) == 0: # No marks provided
        return

    DumpFileHandler.assure_folder(subfolder, FileType.marks)
    fname = DumpFileHandler.get_fname(name, subfolder, tipo=FileType.marks)

    df = pd.DataFrame()
    df[info.times_column] = times
    df[info.messages_column] = messages

    df.to_csv(fname)
    basic.report("Marks saved to file: {}".format(fname))

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
