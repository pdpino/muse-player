#!/usr/bin/env python
"""Decode the bluetooth protocol of Muse"""



def main():
    """Decode a bluetooth message from Muse into readable chars

    Works for the messages received in 0x000e handle.
    Usually they are a series of packets, that together conform a dictionary (key, value pairs)."""

    # El archivo tiene en cada linea un msje, puede estar comenzado por *, cada byte lo tiene separado por un :
        # llegar y copiar desde wireshark
        # ejemplo:
        # * ab:12:34:ef
    fname = "debug.txt"
    with open(fname, "r") as f:
        a = f.readlines()

    verbose = False

    # Decodificar string
    big_string = "" # String completo, concatenando cada mensaje

    for linea in a: # Recorrer cada mensaje
        ## Trim espacios y *
        l = linea.strip().strip("*")

        ## Separar en bytes
        nums = l.split(":")

        ## Recorrer cada byte
        i = 0 # contador
        add_to_str = True # bool que indica si añadir al string completo
        stop_adding = -1 # posicion en la que se dejo de añadir
        for b in nums:
            # Transformar el byte a numero y a un char legible
            x = int(b, 16)
            c = chr(x)

            # El primer byte no es legible (timestamp?, cmd?, no se sabe) --> i > 0
            # En algun momento se llega a una ',' o '}'; significa que la parte importante del msje termino
            if i > 0 and add_to_str:
                if verbose:
                    print(c, end="")
                big_string += c
                if c == ',' or c == '}': # msje termino
                    # de ahi en adelante es basura, de hecho reusan el string asi que es lo mismo que el anterior
                    stop_adding = i
                    add_to_str = False

            i += 1


        if verbose:
            print("")
        # if stop_adding != -1:
        #     print("\tStopped adding at pos {}".format(stop_adding))

        if verbose:
            # Imprimir cada byte leido y su transformacion a int base 10
            for b in nums:
                c = int(b, 16)
                print("\t{}->{}".format(b, c))
            print("\n")

    # El bigstring se ve como un dictionary, pares key value:
    # {"key": "value", ...}
    print(big_string)


if __name__ == "__main__":
    main()
