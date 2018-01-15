"""Facade for filesystem functions."""
from .eeg import *
from .feel import *
from .tf import *
from .marks import *

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
    TFFileHandler.save(filename, dataframe, channel=channel, **fname_kwargs)

def load_tf(filename, channel, **fname_kwargs):
    return TFFileHandler.load(filename, channel=channel, **fname_kwargs)

def exist_tf(filename, channel):
    return TFFileHandler.exist(filename, channel=channel)

def save_marks(filename, timestamps, messages, **fname_kwargs):
    MarksFileHandler.save(filename, timestamps, messages, **fname_kwargs)

def load_marks(filename, **fname_kwargs):
    return MarksFileHandler.load(filename, **fname_kwargs)

def copy_marks(name1, name2):
    MarksFileHandler.copy(name1, name2)
