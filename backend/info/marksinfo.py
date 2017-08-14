"""Info about the marks."""

# Marks standard names
start_calib_mark = "calibrating"
stop_calib_mark = "stop calibrating"

def is_stop_mark(mark):
    """Boolean indicating if is a stop mark."""
    return mark.startswith("stop")

# Names for the columns in marks file
times_column = "times"
messages_column = "messages"
