class FeelYielder:
    """Yields feeling found in the waves."""

    def __init__(self):
        # HACK: use formatter
        self.yield_string = "data: {}, {}, {}\n\n"

    def has_start_message(self):
        return True

    def start_message(self):
        return "event: config\ndata: feel\n\n"

    def generate(self, timestamp, feeling):
        yield self.yield_string.format(timestamp, feeling[0], feeling[1])
