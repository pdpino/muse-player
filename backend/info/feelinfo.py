"""Info about the feelings."""

colname_relaxation = "Relaxation"
colname_concentration = "Concentration"

colname_arousal = "arousal"
colname_valence = "valence"

def get_feelings_colnames():
    # DEPRECATED: Relaxation and Concentration are not the only feelings anymore
    # FIXME
    return [colname_relaxation, colname_concentration]
