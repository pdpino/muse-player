"""Utility functions for this module."""
from backend import basic

def _compare_channels(real_chs, wanted_chs):
    """Compare the existing channels with the wanted ones, return the intersection and notifies the difference."""
    # Make sets
    real_chs = set(real_chs)
    wanted_chs = set(wanted_chs)

    eff_chs = list(real_chs.intersection(wanted_chs)) # effective channels
    none_chs = list(wanted_chs - real_chs) # non existing channels
    if len(none_chs) > 0:
        basic.perror("The channel '{}' is not in the loaded file".format(ch), force_continue=True)

    return eff_chs
