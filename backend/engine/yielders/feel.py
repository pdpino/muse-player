from . import base

class FeelYielder(base.BaseYielder):
    """Yields feeling found in the waves."""

    def __init__(self):
        # HACK: use formatter
        self.yield_string = "data: {}, {}, {}\n\n"

        self.config_data = "feel"

    def generate(self, timestamp, feeling):
        yield self.yield_string.format(timestamp, feeling[0], feeling[1])
