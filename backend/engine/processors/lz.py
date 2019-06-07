import numpy as np
from . import base

def LZ76(arr):
    """
    Calculate Lempel-Ziv's algorithmic complexity using the LZ76 algorithm
    and the sliding-window implementation.

    Reference:

    F. Kaspar, H. G. Schuster, "Easily-calculable measure for the
    complexity of spatiotemporal patterns", Physical Review A, Volume 36,
    Number 2 (1987).

    Input:
      arr -- array of integers

    Output:
      c  -- integer
    """

    ss = 1*(arr > np.median(arr))

    i, k, l = 0, 1, 1
    counter, k_max = 1, 1
    n = len(ss)
    while True:
        if ss[i + k - 1] == ss[l + k - 1]:
            k = k + 1
            if l + k > n:
                counter = counter + 1
                break
        else:
            if k > k_max:
               k_max = k
            i = i + 1
            if i == l:
                counter = counter + 1
                l = l + k_max
                if l + 1 > n:
                    break
                else:
                    i = 0
                    k = 1
                    k_max = 1
            else:
                k = 1
    return counter

class LZProcessor(base.BaseProcessor):
    """Process the EEG transforming it into waves.

    TODO"""

    def __init__(self, generator):
        """Constructor."""
        self.generator = generator

    def generate(self, timestamp, new_data):
        """Calculates LZ by channel and yields the result."""
        n_channels, window_size = new_data.shape

        normalizer = np.log(window_size)/window_size

        lzs = []
        for ch_index in range(4):
            lz = LZ76(new_data[ch_index]) * normalizer
            lzs.append(lz)

        timestamp = round(timestamp)

        # DEBUG: print values to stdout
        print(timestamp, lzs)

        yield from self.generator.generate(timestamp, lzs)
