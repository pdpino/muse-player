"""Info about the _waves."""
from collections import OrderedDict
import numpy as np

# OrderedDict with
# key: wave_name -- value: [min_freq, max_freq, color]
# used to plot always with the same colors and the same order
_waves = OrderedDict([["delta", [1, 4, "blue"]],
                     ["theta", [4, 8, "orange"]],
                     ["alpha", [8, 13, "red"]],
                     ["beta", [13, 30, "green"]],
                     ["lbeta", [13, 20, "purple"]], # low beta
                     ["hbeta", [20, 30, "brown"]], # high beta
                     ["gamma", [30, 44, "magenta"]]
                     ])

# NOTE: for the matplotlib colors see https://matplotlib.org/examples/color/named_colors.html

def get_amount_waves():
    return len(_waves)

def get_waves_names(choose=None):
    """Return a list with the waves names. If choose is given, only those in choose will be returned"""
    if choose is None:
        return list(_waves)
    else:
        # NOTE: not using sets because it loses the order from the OrderedDict
        return [w for w in list(_waves) if w in choose]

def iter_waves(waves=None):
    """Iterate over the waves names and freqs limits."""
    for wave_name in list(waves or _waves):
        min_freq = _waves[wave_name][0]
        max_freq = _waves[wave_name][1]
        yield wave_name, min_freq, max_freq

def filter_freqs(freqs, min_freq, max_freq):
    """Return filtered freqs given two borders."""
    return [f for f in freqs if float(f) >= min_freq and float(f) <= max_freq]

def get_freqs_filter(freqs, min_freq, max_freq):
    """Return a filter over a numpy array."""
    filter_freqs, = np.where((freqs >= min_freq) & (freqs <= max_freq))
    return filter_freqs

def get_wave_color(wave):
    """Given a wave_name, get the color."""
    if wave in _waves:
        return _waves[wave][2]

    return None
