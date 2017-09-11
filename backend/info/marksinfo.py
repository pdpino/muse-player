"""Info about the marks."""

# Marks standard names
start_calib_mark = "calibrating"
stop_calib_mark = "stop calibrating"

start_collect_mark = "collecting"
stop_collect_mark = "stop collecting"

def is_stop_mark(mark):
    """Boolean indicating if is a stop mark."""
    return mark.startswith("stop")

def is_calib_mark(mark):
    return mark == start_calib_mark or mark == start_collect_mark

# Names for the columns in marks file
times_column = "times"
messages_column = "messages"
