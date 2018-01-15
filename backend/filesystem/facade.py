"""Facade for filesystem functions."""
from .eeg import *
from .feel import *

def save_eeg(filename, dataframe, **fname_kwargs):
    EEGFilesystem.save(filename, dataframe, **fname_kwargs)

def load_eeg(filename, channels=None, **fname_kwargs):
    timestamps, df, channels = EEGFilesystem.load(filename, channels, **fname_kwargs)
    return timestamps, df, channels

def save_feelings(filename, dataframe, **fname_kwargs):
    FeelFilesystem.save(filename, dataframe, **fname_kwargs)

def load_feelings(filename, **fname_kwargs):
    timestamps, df = FeelFilesystem.load(filename, **fname_kwargs)
    return timestamps, df
