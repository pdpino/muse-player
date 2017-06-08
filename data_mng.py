#!/usr/bin/env python
"""Layer that handles the data"""
import os
import pandas as pd

data_folder = "data/"
data_ext = ".csv"

def _assure_folder(path):
    """Assure the existence of a given folder"""
    if not os.path.exists(path):
        os.makedirs(path)

def _get_fname(name, subfolder=None):
    """Return the full filename for a data file"""
    fname = data_folder
    if not subfolder is None:
        fname += subfolder + "/"
        _assure_folder(fname)

    fname += name

    if not fname.endswith(data_ext):
        fname += data_ext

    return fname

def read_data(name, subfolder=None):
    """Read a .csv file and returns the dataframe"""
    fname = _get_fname(name, subfolder)

    try:
        df = pd.read_csv(fname, index_col=0)
        print("Read from file: {}".format(fname))
        return df
    except FileNotFoundError:
        print("")


def save_data(df, name, subfolder=None):
    """Save a dataframe to a .csv"""
    fname = _get_fname(name, subfolder)

    df.to_csv(fname, float_format='%f')
    print("Saved to file: {}".format(fname))
