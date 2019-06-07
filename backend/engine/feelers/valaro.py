import numpy as np
from backend import tf, info
from . import base

class FeelerValAro(base.BaseFeeler):
    """Map frequencies to Valence and Arousal map.

    The formulas used are:
    arousal = ABratio_t(4) - ABratio_t(3)
    valence = ABratio(4) - ABratio(3)

    Where:
    ABratio_t(x) = (B(AFx) + B(Fx)) / (A(AFx) + A(Fx))
    ABratio(x) = B(AFx) / A(AFx)
    B(x) is Beta wave from channel x
    A(x) is Alpha wave from channel x

    AF3 and AF4 are replaced by AF7 and AF8
    F3 and F4 are replaced by TP9 and TP10
    """

    def __init__(self, window=256, srate=256):
        self.config_data = {
            'categories': [{
                'name': 'Valence',
                'color': '#a50f15'
            }, {
                'name': 'Arousal',
                'color': '#3690c0'
            }],
            'yAxisLabel': 'Measure of emotion',
            'title': 'Emotion',
            'yAutoUpdate': True,
        }

        # Channel numbers
        self._tp9 = info.get_channel_number('TP9')
        self._af7 = info.get_channel_number('AF7')
        self._af8 = info.get_channel_number('AF8')
        self._tp10 = info.get_channel_number('TP10')

        # Wave filters
        self.arr_freqs = tf.get_freqs_resolution(window, srate)
        self._alpha_filter = info.get_freqs_filter(self.arr_freqs, 8, 13)
        self._beta_filter = info.get_freqs_filter(self.arr_freqs, 13, 30)

    def get_names(self):
        return [info.colname_arousal, info.colname_valence]

    def calculate(self, power):
        """Transform power into a valence and arousal status."""

        get_band = lambda channel, band_filter: np.mean(power[channel, band_filter])

        # Calculate band powers
        alpha_af7 = get_band(self._af7, self._alpha_filter)
        beta_af7 = get_band(self._af7, self._beta_filter)
        alpha_af8 = get_band(self._af8, self._alpha_filter)
        beta_af8 = get_band(self._af8, self._beta_filter)

        alpha_tp9 = get_band(self._tp9, self._alpha_filter)
        beta_tp9 = get_band(self._tp9, self._beta_filter)
        alpha_tp10 = get_band(self._tp10, self._alpha_filter)
        beta_tp10 = get_band(self._tp10, self._beta_filter)

        # Average for both channels
        arousal = (beta_af8 + beta_tp10) / (alpha_af8 + alpha_tp10) - (beta_af7 + beta_tp9) / (alpha_af7 + alpha_tp9)
        valence = beta_af8 / alpha_af8 - beta_af7 / alpha_af7

        return [arousal, valence]

    def pack_data(self, timestamp, feeling):
        yield [{
            'name': 'Arousal',
            'value': feeling[0]
        }, {
            'name': 'Valence',
            'value': feeling[1]
        }]
