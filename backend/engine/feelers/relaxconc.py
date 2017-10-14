import numpy as np
from backend import tf, info
from . import base

class FeelerRelaxConc(base.Feeler):
    """Feels relaxation and concentration.

    alpha from ear channels is relaxation
    beta from forehead channels is concentration"""

    def __init__(self, window=256, srate=256):
        self.arr_freqs = tf.get_freqs_resolution(window, srate)

        self.config_data = "feel"

        # HACK: use formatter
        self.yield_string = "data: {}, {}, {}\n\n"

    def calculate(self, power):
        """Transform power into a relaxation and concentration status."""

        # Alpha for earback channels (TP9 and TP10)
        flat_alpha = power[0::3, info.get_freqs_filter(self.arr_freqs, 8, 13)].flatten()

        # Beta for forehead channels (AF7 and AF8)
        flat_beta = power[1:3, info.get_freqs_filter(self.arr_freqs, 13, 30)].flatten()

        # Average for both channels
        relaxation = np.mean(flat_alpha)
        concentration = np.mean(flat_beta)

        return [relaxation, concentration]

    def generate(self, timestamp, feeling):
        yield self.yield_string.format(timestamp, feeling[0], feeling[1])
