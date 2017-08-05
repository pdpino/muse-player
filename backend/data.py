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

def load_eeg(name, subfolder=None, suffix=None):
    """Read a .csv file and return the dataframe"""
    fname = DumpFileHandler.get_fname(name, subfolder, suffix)

    try:
        df = pd.read_csv(fname, index_col=0)
        basic.report("EEG loaded from file: {}".format(fname))
        return df
    except FileNotFoundError:
        basic.perror("The file {} wasn't found".format(fname))

def save_eeg(df, name, subfolder=None, suffix=None):
    """Save a dataframe to a .csv"""
    DumpFileHandler.assure_folder(subfolder)
    fname = DumpFileHandler.get_fname(name, subfolder, suffix)

    # TODO: revisar que la primera columna sea timestamps
    df.to_csv(fname, float_format='%f') #, index_label='timestamps')
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
        basic.perror("The file {} wasn't found".format(fname), force_continue=True)
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
