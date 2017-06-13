#!/usr/bin/env python
"""Layer that handles the data"""
import os
import pandas as pd
import basic

data_folder = "data/"
data_ext = ".csv"

def _assure_folder(path):
    """Assure the existence of a given folder"""
    if not os.path.exists(path):
        os.makedirs(path)

def _get_fname(name, subfolder=None, suffix=None, assure=False):
    """Return the full filename for a data file

    Parameters:
    subfolder --
    suffix --
    assure -- bool, whether to assure the existence of the subfolder or not"""


    fname = data_folder
    if not subfolder is None:
        fname += subfolder + "/"
        if assure:
            _assure_folder(fname)

    if name is None or name == "":
        fname += "-"
    else:
        fname += name

    if not suffix is None:
        fname += "_" + str(suffix) # Ejemplo: data_1, data_2, etx

    if not fname.endswith(data_ext):
        fname += data_ext

    return fname

def read_data(name, subfolder=None, suffix=None):
    """Read a .csv file and returns the dataframe"""
    fname = _get_fname(name, subfolder, suffix)

    try:
        df = pd.read_csv(fname, index_col=0)
        print("Read from file: {}".format(fname))
        return df
    except FileNotFoundError:
        basic.perror("The file {} wasn't found".format(fname))


def save_data(df, name, subfolder=None, suffix=None):
    """Save a dataframe to a .csv"""
    fname = _get_fname(name, subfolder, suffix, assure=True)

    df.to_csv(fname, float_format='%f')
    print("Saved to file: {}".format(fname))
