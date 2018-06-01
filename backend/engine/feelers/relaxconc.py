import numpy as np
from backend import tf, info
from . import base

class FeelerRelaxConc(base.BaseFeeler):
    """Feels relaxation and concentration.

    alpha from ear channels is relaxation
    beta from forehead channels is concentration"""

    def __init__(self, window=256, srate=256, moodplay=False):
        """

        moodplay -- boolean indicating if streaming to moodplay instead of muse-player
        """
        self.config_data = {
            'categories': [{
                'name': 'Concentration',
                'color': '#e6550d' #'#a50f15'
            }, {
                'name': 'Relaxation',
                'color': '#31a354' # '#3690c0'
            }],
            'yAxisLabel': 'Measure of state', # REVIEW: change key names?
            'title': 'State of mind'
        }

        # Band filters
        self.arr_freqs = tf.get_freqs_resolution(window, srate)
        self._alpha_filter = info.get_freqs_filter(self.arr_freqs, 8, 13)
        self._beta_filter = info.get_freqs_filter(self.arr_freqs, 13, 30)

        # Data to normalize
        self.min_feeling = None
        self.max_feeling = None

        # Don't pack timestamp when streaming to moodplay
        self.moodplay = moodplay
        if self.moodplay:
            self.pack_timestamp = self._dont_pack_timestamp

    def get_names(self):
        return [info.colname_relaxation, info.colname_concentration]

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

    def normalize_range(self, value):
        """Move the values to between 0 and 1"""
        # return (value - self.min_feeling) / (self.max_feeling - self.min_feeling)
        min_value = -5
        max_value = 5
        new_value = (value - min_value) / (max_value - min_value)
        return new_value / 5

    def _dont_pack_timestamp(self, timestamp, packed_data):
        """Override method to not pack any timestamp.

        This fixes that moodplay needs that a timestamp does not come
        REVIEW: move this to BaseFeeler? be able to set self.no_timestamp = True
        """
        pass

    def pack_data(self, timestamp, feeling):
        """Pack concentration and relaxation data."""
        # print(feeling)

        # Save first normalization
        # if self.max_feeling is None or self.min_feeling is None:
        #     self.max_feeling = feeling[0]
        #     self.min_feeling = feeling[0]

        # Update normalization values
        # for feel in feeling:
        #     if feel > self.max_feeling:
        #         self.max_feeling = feel
        #     elif feel < self.min_feeling:
        #         self.min_feeling = feel

        # Normalize between -5 and 5
        relaxation = self.normalize_range(feeling[0])
        concentration = self.normalize_range(feeling[1])


        # Square to accentuate
        # relaxation = relaxation ** 2
        # concentration = concentration ** 2

        # Softmax
        if self.moodplay:
            relaxation, concentration = calculate_softmax(relaxation, concentration)

        # print(relaxation, concentration)

        yield [{
            'name': 'Concentration',
            'value': concentration
        }, {
            'name': 'Relaxation',
            'value': relaxation
        }]


def calculate_softmax(x, y):
    e_x = np.exp(x)
    e_y = np.exp(y)
    total_exp = e_x + e_y

    x_norm = e_x / total_exp
    y_norm = e_y / total_exp
    return x_norm, y_norm
