"""Info about eeg data."""

timestamps_column = 'timestamps'

def get_chs_muse(aux):
    """Get the channel names in muse order. aux indicates if include auxiliary channel"""
    _ch_names = ['TP9', 'AF7', 'AF8', 'TP10', 'Right Aux']
    if aux:
        return _ch_names
    else: # Exclude aux channel
        return _ch_names[:-1]

def get_chs_plot(chs=None):
    """Return the channel names in the plotting order."""
    _ch_names_plot = ['TP9', 'TP10', 'AF7', 'AF8']
    if chs is None:
        return _ch_names_plot
    else:
        return [c for c in _ch_names_plot if c in chs] # Return them in the plot order
