#!/usr/bin/env python
"""Plot the saved data with python. Used for testing"""


import sys
import pandas
import argparse
from matplotlib import pyplot as plt

if __name__ == "__main__":
    ##### Parsear argumentos
    parser = argparse.ArgumentParser(description='Plot dump.csv data', usage='%(prog)s [options]')
    parser.add_argument('-c', '--channel', default="AF7", type=str,
                        help="Channel to plot. Options: TP9, TP10, AF7, AF8, 'Right Aux'")

    args = parser.parse_args()

    # Leer csv
    df = pandas.DataFrame.from_csv("data/dump.csv")

    # Plot
    x = df["timestamps"]
    try:
        y = df[args.channel]
    except:
        print("Wrong channel")
        sys.exit(1)

    plt.plot(x, y)
    plt.show()
