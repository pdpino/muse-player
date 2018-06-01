"""Info about eeg data."""

colname_timestamps = 'timestamps'

# All channels
_ch_names = ['TP9', 'AF7', 'AF8', 'TP10', 'Right Aux']
# Channels used to plot
_ch_names_plot = ['TP9', 'TP10', 'AF7', 'AF8']

# Channel numbers
_ch_numbers = {
    'TP9': 0,
    'AF7': 1,
    'AF8': 2,
    'TP10': 3,
    'Right Aux': 4
    }

def get_chs_muse(aux):
    """Get the channel names in muse order. aux indicates if include auxiliary channel"""
    if aux:
        return _ch_names
    else: # Exclude aux channel
        return _ch_names[:-1]

def get_chs_plot(chs=None):
    """Return the channel names in the plotting order."""
    if chs is None:
        return _ch_names_plot
    else:
        return [c for c in _ch_names_plot if c in chs] # Return them in the plot order

def get_channel_number(channel_name):
    """Return the channel number. Default value is 0"""
    return _ch_numbers.get(channel_name, 6)

def get_channel_numbers():
    """Return a copy of the dict that has the channel numbers."""
    return dict(_ch_numbers)

def get_channel_name(channel_number):
    if channel_number is None:
        print('WARNING: channel is none', channel_number)
        return 'Channel'
    if channel_number >= len(_ch_names):
        print('WARNING: no channel with number', channel_number)
        return 'Channel {}'.format(channel_number)
    return _ch_names[channel_number]
