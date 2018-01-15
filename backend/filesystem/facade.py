"""Facade for filesystem functions."""
from .eeg import *
from .feel import *
from .tf import *

def save_eeg(filename, dataframe, **fname_kwargs):
    EEGFileHandler.save(filename, dataframe, **fname_kwargs)

def load_eeg(filename, channels=None, **fname_kwargs):
    timestamps, df, channels = EEGFileHandler.load(filename, channels, **fname_kwargs)
    return timestamps, df, channels

def save_feelings(filename, dataframe, **fname_kwargs):
    FeelFileHandler.save(filename, dataframe, **fname_kwargs)

def load_feelings(filename, **fname_kwargs):
    timestamps, df = FeelFileHandler.load(filename, **fname_kwargs)
    return timestamps, df

def save_tf(filename, dataframe, channel, **fname_kwargs):
    FeelFileHandler.save(filename, dataframe, channel=channel, **fname_kwargs)

def load_tf(filename, channel, **fname_kwargs):
    return FeelFileHandler.load(filename, channel=channel, **fname_kwargs)
