"""Info about the _waves."""
from collections import OrderedDict

# OrderedDict with the _waves min_freq and max_freq
_waves = OrderedDict([["delta", (1, 4)],
                     ["theta", (4, 8)],
                     ["alpha", (8, 13)],
                     ["beta", (13, 30)],
                     ["lbeta", (13, 20)], # low beta
                     ["hbeta", (20, 30)], # high beta
                     ["gamma", (30, 44)]
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
