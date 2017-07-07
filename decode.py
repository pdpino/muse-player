#!/usr/bin/env python3
"""Script to try decoding the accelerometer/battery/etc packets."""
import pandas as pd
import numpy as np
import struct
import array
from enum import Enum

class NumTypes(Enum):
    int32 = 0
    uint32 = 1
    int16 = 2
    uint16 = 3
    float16 = 4

def get_tipo(tipo):
    if tipo == NumTypes.int32:
        return 'i'
    elif tipo == NumTypes.uint32:
        return 'I'
    elif tipo == NumTypes.int16:
        return 'h'
    elif tipo == NumTypes.uint16:
        return 'H'
    elif tipo == NumTypes.float16:
        return 'e'
    else:
        return 'i' # default int 32

def main():
    """Try decode handle 14."""
    fname = "debug/debug_handle14_v2.csv" # XXX
    df = pd.read_csv(fname, header=None)

    # Tomar matrix de bytes
    n_cols = 9 # XXX
    bytes_cols = [i + 1 for i in range(n_cols)]
    bt = df[bytes_cols]

    # Nueva matrix para guardar decodificacion
    n_rows = len(bt.index)
    matrix = np.zeros((n_rows, n_cols))

    def parse_byte(b, parser):
        """Parse a str_byte to a certain type of data (int, uint, etc).

        Receives 4 bytes (16bits).
        Types:
        i -- int 32
        I -- uint 32
        h -- short (int 16)
        H -- unsigned short (uint 16)
        e -- float 16 (added in python 3.6)
        """
        def str_to_barr(s):
            """Receive a string and transform it to bytearray."""
            # HACK:
            nums = []
            for i in [s[:2], s[2:]]: # Separate in two strings of 2 letters (1 byte each)
                nums.append(int(i, 16)) # Transform to int
            return bytearray(nums) # Transform to bytearray

        d = struct.unpack(parser, str_to_barr(b))
        return d[0] # first of the tuple

    # Como parsear
    tipo = get_tipo(NumTypes.float16)

    # Recorrer dataframe
    for row in range(n_rows):
        i_col = 0
        for col in bytes_cols:
            str_byte = str(bt.loc[row, col]) # HACK: copy value # neccesary?
            matrix[row, i_col] = parse_byte(str_byte, tipo)
            i_col += 1

    # Pass new matrix to dataframe
    parsed_df = pd.DataFrame(matrix)

    # Save to file
    fname = "debug/parsed_handle14_v2_{}.csv".format(tipo)
    parsed_df.to_csv(fname) #, float_format='%.2f')

if __name__ == "__main__":
    main()
