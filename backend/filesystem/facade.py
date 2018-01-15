"""Facade for filesystem functions."""
from .eeg import *

def save_eeg(filename, eeg_dataframe):
    EEGFilesystem.save(filename, eeg_dataframe)

def load_eeg(filename, channels=None):
    times, df, channels = EEGFilesystem.load(filename, channels)
    return times, df, channels
