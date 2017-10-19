"""Module that stores parser common arguments."""
import argparse
from backend import info

# REVIEW: esto no es backend!

def add_file_args(parser, fsave=False):
    """Add file arguments to a parser.

    if fsave add a second filename argument (to save with a different name)"""
    group_data = parser.add_argument_group(title="File arguments")
    group_data.add_argument('-f', '--fname', default="data", type=str, help="Name of the .csv file")
    if fsave:
        group_data.add_argument('--fsave', default=None, type=str, help="Name to save, if None, use fname")

    group_data.add_argument('--subfolder', default=None, type=str, help="Subfolder to read the .csv file")

def add_ch_args(parser, aux=False):
    """Add channel argument."""
    parser.add_argument('--channels', choices=info.get_chs_muse(aux=aux), default=None, nargs='+', help="Select channels")
