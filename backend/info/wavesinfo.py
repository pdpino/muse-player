"""Info about the _waves."""
from collections import OrderedDict

# OrderedDict with the _waves min_freq and max_freq
_waves = OrderedDict([["delta", [1, 4, "blue"]],
                     ["theta", [4, 8, "orange"]],
                     ["alpha", [8, 13, "red"]],
                     ["beta", [13, 30, "green"]],
                     ["lbeta", [13, 20, "purple"]], # low beta
                     ["hbeta", [20, 30, "brown"]], # high beta
                     ["gamma", [30, 44, "magenta"]]
                     ])

def get_waves_names(choose=None):
    """Return a list with the waves names. If choose is given, only those in choose will be returned"""
    if choose is None:
        return list(_waves)
    else:
        filtered_waves = [w for w in list(_waves) if w in choose]
        # NOTE: not using sets because it loses the order from the OrderedDict
        return filtered_waves

def iter_waves():
    """Iterate over the waves names and limits."""
    for w in list(_waves):
        min_freq = _waves[w][0]
        max_freq = _waves[w][1]
        yield w, min_freq, max_freq

def filter_freqs(freqs, min_freq, max_freq):
    return [f for f in freqs if float(f) >= min_freq and float(f) <= max_freq]

def get_wave_color(wave):
    """Given a wave_name, get the color."""
    if wave in _waves:
        # REVIEW: check if color exist? a wave may not have a color
        return _waves[wave][2]

    return None
