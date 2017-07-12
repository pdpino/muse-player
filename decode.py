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

def read_h14():
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

def read_h14_bin():
    """Try decode handle 14."""
    fname = "debug/handle14_bin.csv" # XXX
    df = pd.read_csv(fname, header=None)

    # Tomar lista de todos los strings
    all_bits = df[1]

    # Parametros # XXX
    di = 16 # Saltar de 16 en 16
    bits_time = 16 # bits de timestamp
    bits_totales = 160 # msje total tiene eso

    # Matrix vacia para guardar
    n_chunks = (bits_totales - bits_time) // di # numeros por cada msje
    n_rows = len(all_bits) # cantidad de mensajes
    # matrix = np.zeros((n_rows, n_chunks))

    matrix = []
    tiempos = []

    # Recorrer
    row = 0
    for str_bits in all_bits:
        n = len(str_bits)

        # Leer tiempo
        i = 0
        t = str(str_bits[i:i+bits_time])
        i += bits_time
        tiempos.append(t)

        # Leer numeros
        col = 0
        fila = []
        while i < n:
            sl = str_bits[i:i+di] # tomar slice
            a = str(sl) # transformar # TODO
            # matrix[row, col] = a
            fila.append(a)
            i += di
            col += 1

        matrix.append(fila)

        row += 1


    # Print matrix
    print_matrix = False
    if print_matrix:
        for row in range(n_rows):
            print(tiempos[row], end=", ")
            for col in range(n_chunks):
                print(matrix[row][col], end=", ")

            print("")


    # Transformar a numero
    matrix_nums = np.zeros((n_rows, n_chunks + 1)) # +1 x el tiempo
    for row in range(n_rows):
        t = int(tiempos[row], 2)
        matrix_nums[row, 0] = t
        for col in range(n_chunks):
            i_col = col + 1
            num_bits = matrix[row][col]

            # Pack it
            num_int = int(num_bits, 2)
            packed = struct.pack('h', num_int)

            # Unpack it
            num_float, = struct.unpack('e', packed)

            # save it
            matrix_nums[row, i_col] = num_float


    # Concatenar cols 1,2,3 con 4,5,6 con 7,8,9
    concat = False
    if concat:
        full_rows = n_rows*3
        full_cols = n_chunks // 3 + 1
        matrix_concat = np.zeros((full_rows, full_cols))

        row1 = 0 # recorre matrix original
        row2 = 0 # recorre segunda matrix
        while row1 < n_rows:
            # Copiar tiempo 3 veces seguidas
            t = int(tiempos[row1], 2)
            for i in range(3):
                row2 += i
                matrix_concat[row2, 0] = t

            # Colocar numeros # TODO

            row1 += 1


            # matrix_nums[row, 0] = t
            # for col in range(n_chunks):
            #     i_col = col + 1
            #     m = int(matrix[row][col], 2)
            #     matrix_nums[row, i_col] = m




    df = pd.DataFrame(matrix_nums)
    print(df)


    # Save to file
    fname = "debug/parsed_handle14_bin.csv"
    df.to_csv(fname) #, float_format='%.2f')


if __name__ == "__main__":
    read_h14_bin()
