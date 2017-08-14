"""Info about eeg data."""

timestamps_column = 'timestamps'

def ch_names_muse(aux):
    """Return the channel names in muse order. aux indicates if include auxiliary channel"""
    _ch_names = ['TP9', 'AF7', 'AF8', 'TP10', 'Right Aux']
    if aux:
        return _ch_names
    else: # Exclude aux channel
        return _ch_names[:-1]

def ch_names_plot():
    """Return the channel names in the plotting order."""
    return ['TP9', 'TP10', 'AF7', 'AF8']
