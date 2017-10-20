"""Handle marks files."""
import shutil
import pandas as pd
from backend import info
import basic
from . import filehandler as fh

def load_marks(name, subfolder=None):
    """Read a marks file."""
    fname = fh.DumpFileHandler.get_fname(name, subfolder, tipo=fh.FileType.marks)

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

    fh.DumpFileHandler.assure_folder(subfolder, fh.FileType.marks)
    fname = fh.DumpFileHandler.get_fname(name, subfolder, tipo=fh.FileType.marks)

    df = pd.DataFrame()
    df[info.times_column] = times
    df[info.messages_column] = messages

    df.to_csv(fname)
    basic.report("Marks saved to file: {}".format(fname))

def copy_marks(name1, name2):
    """Copy a marks file."""
    fh.DumpFileHandler.assure_folder(None, fh.FileType.marks)
    fname1 = fh.DumpFileHandler.get_fname(name1, None, tipo=fh.FileType.marks)
    fname2 = fh.DumpFileHandler.get_fname(name2, None, tipo=fh.FileType.marks)

    shutil.copyfile(fname1, fname2)
