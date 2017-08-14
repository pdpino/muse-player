"""Module that stores parser common arguments."""
import argparse
from backend import data

# REVIEW: esto no es backend!

def add_file_args(parser):
    """Add file arguments to a parser."""
    group_data = parser.add_argument_group(title="File arguments")
    group_data.add_argument('-f', '--fname', default="data", type=str, help="Name of the .csv file to read")
    group_data.add_argument('--subfolder', default=None, type=str, help="Subfolder to read the .csv file")

def add_ch_args(parser, aux=False):
    """Add channel argument."""
    parser.add_argument('--channels', choices=data.ch_names(aux=aux), default=None, nargs='+', help="Select channels")
