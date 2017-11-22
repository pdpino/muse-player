import numpy as np
from backend import tf, info
from . import base

class FeelerRelaxConc(base.Feeler):
    """Feels relaxation and concentration.

    alpha from ear channels is relaxation
    beta from forehead channels is concentration"""

    def __init__(self, window=256, srate=256):
        # self.config_data = "feel" # DEPRECATED
        self.config_data = {
            'categories': [{
                'name': 'Concentration',
                'color': '#a50f15'
            }, {
                'name': 'Relaxation',
                'color': '#3690c0'
            }]
        }

        # Band filters
        self.arr_freqs = tf.get_freqs_resolution(window, srate)
        self._alpha_filter = info.get_freqs_filter(self.arr_freqs, 8, 13)
        self._beta_filter = info.get_freqs_filter(self.arr_freqs, 13, 30)

        # Data to normalize
        self.min_feeling = None
        self.max_feeling = None


        # HACK: use formatter
        # self.yield_string = "data: {}, {}, {}\n\n" # DEPRECATED

    def calculate(self, power):
        """Transform power into a relaxation and concentration status."""

        # Alpha for earback channels (TP9 and TP10)
        flat_alpha = power[0::3, self._alpha_filter].flatten()

        # Beta for forehead channels (AF7 and AF8)
        flat_beta = power[1:3, self._beta_filter].flatten()

        # Average for both channels
        relaxation = np.mean(flat_alpha)
        concentration = np.mean(flat_beta)

        return [relaxation, concentration]

    # DEPRECATED
    # def generate(self, timestamp, feeling):
    #     yield self.yield_string.format(timestamp, feeling[0], feeling[1])

    def normalize_range(self, value):
        """Move the values to between 0 and 1"""
        return (value - self.min_feeling) / (self.max_feeling - self.min_feeling)

    def pack_data(self, timestamp, feeling):
        """Pack concentration and relaxation data."""
        print(feeling)

        # Save first normalization
        if self.max_feeling is None or self.min_feeling is None:
            self.max_feeling = feeling[0]
            self.min_feeling = feeling[0]

        # Update normalization values
        for feel in feeling:
            if feel > self.max_feeling:
                self.max_feeling = feel
            elif feel < self.min_feeling:
                self.min_feeling = feel

        # Normalize between 0 and 1
        relaxation = self.normalize_range(feeling[0])
        concentration = self.normalize_range(feeling[1])

        # Normalize to add up to 1
        total = relaxation + concentration
        relaxation /= total
        concentration /= total

        return [{
            'name': 'Concentration',
            'value': concentration
        }, {
            'name': 'Relaxation',
            'value': relaxation
        }]
