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
        return cls._get_fname(lname, folder=subfolder, suffix=suffix, ext=cls.get_ext(status))

    @classmethod
    def assure_folder(cls, subfolder):
        """Assure the existence of a folder."""
        cls._assure_folder(subfolder)

def read_data(name, subfolder=None, suffix=None):
    """Read a .csv file and returns the dataframe"""
    fname = DumpFileHandler.get_fname(name, subfolder, suffix)

    try:
        df = pd.read_csv(fname, index_col=0)
        print("Read from file: {}".format(fname))
        return df
    except FileNotFoundError:
        basic.perror("The file {} wasn't found".format(fname))

def save_data(df, name, subfolder=None, suffix=None):
    """Save a dataframe to a .csv"""
    DumpFileHandler.assure_folder(subfolder)
    fname = DumpFileHandler.get_fname(name, subfolder, suffix)

    df.to_csv(fname, float_format='%f')
    print("Saved to file: {}".format(fname))
