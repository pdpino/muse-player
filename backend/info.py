"""Store useful info for multiple modules and scripts."""
from collections import OrderedDict

# OrderedDict with the waves min_freq and max_freq
waves = OrderedDict([["delta", (1, 4)],
                     ["theta", (4, 8)],
                     ["alpha", (8, 13)],
                     ["beta", (13, 30)],
                     ["gamma", (30, 44)]
                     ])

def get_waves_names(choose=None):
    """Return a list with the waves names. If choose is given, only those in choose will be returned"""
    if choose is None:
        return list(waves)
    else:
        existing_waves = set(waves)
        chosen_waves = set(choose)
        return list(existing_waves.intersection(chosen_waves)) # Return intersection

def iter_waves():
    """Iterate over the waves names and limits."""
    for w in list(waves):
        min_freq = waves[w][0]
        max_freq = waves[w][1]
        yield w, min_freq, max_freq
