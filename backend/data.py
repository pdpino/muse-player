"""Module that provides functionality to manage the data"""
import os
import pandas as pd
import basic

class DumpFileHandler(basic.FileHandler):
    """Handle the dump file and folder names."""

    """Folders."""
    root_folder = "" # HERE
    base_folder = "data"

    """Extension."""
    ext = "csv"

    #### UNUSED METHOD
    # @classmethod
    # def get_folder(cls, subfolder):
    #     """Return the folder."""
    #     return cls._get_folder(subfolder)

    @classmethod
    def get_fname(cls, name, subfolder=None, suffix=None):
        """Return the vocabulary full filename."""
        return cls._get_fname(name, folder=subfolder, suffix=suffix, ext=cls.ext)

    @classmethod
    def assure_folder(cls, subfolder):
        """Assure the existence of a folder."""
        cls._assure_folder(subfolder)

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
    fname = DumpFileHandler.get_fname(name, subfolder, suffix)

    try:
        df = pd.read_csv(fname, index_col=0)
        basic.report("EEG loaded from file: {}".format(fname))
    except FileNotFoundError:
        basic.perror("The file {} wasn't found".format(fname))

    if channels is None:
        # Get all channels
        channels = ch_names()

    # Assure channels in columns
    channels = _cmp_chs(df.columns, channels)
    times = df['timestamps']
    df = df[channels]

    return times, df, channels

def save_eeg(df, name, subfolder=None, suffix=None):
    """Save a dataframe to a .csv"""
    DumpFileHandler.assure_folder(subfolder)
    fname = DumpFileHandler.get_fname(name, subfolder, suffix)

    # TODO: revisar que la primera columna sea timestamps
    df.to_csv(fname, float_format='%f')
    basic.report("EEG saved to file: {}".format(fname))

def load_marks(name, subfolder=None):
    """Read a marks file."""
    fname = DumpFileHandler.get_fname(name, subfolder, "marks") # HACK: marks hardcoded

    try:
        df = pd.read_csv(fname)
        times = list(df['times']) # HACK: times and messages hardcoded
        messages = list(df['messages'])

        basic.report("Marks loaded from file: {}".format(fname))
        return times, messages
    except FileNotFoundError:
        basic.report("Can't find marks file: {}".format(fname))
        return None, None

def save_marks(times, messages, name, subfolder=None):
    """Save marks to a file."""
    if len(times) == 0 or len(messages) == 0: # No marks provided
        return

    DumpFileHandler.assure_folder(subfolder)
    fname = DumpFileHandler.get_fname(name, subfolder, "marks") #HACK: marks hardcoded

    df = pd.DataFrame()
    df['times'] = times # HACK
    df['messages'] = messages

    df.to_csv(fname)
    basic.report("Marks saved to file: {}".format(fname))

_ch_names = ['TP9', 'AF7', 'AF8', 'TP10', 'Right Aux']
def ch_names(aux=False):
    """Return the channel names. aux indicates if include auxiliary channel"""
    if aux:
        return _ch_names
    else: # Exclude aux channel
        return _ch_names[:-1]
