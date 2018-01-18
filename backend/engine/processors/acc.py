import numpy as np
from . import base

class AccProcessor(base.BaseProcessor):
    """Provides a accelerometer processor."""

    def __init__(self, generator, max_accumulate=24):
        """Constructor."""

        self.generator = generator

        # HACK: this should be done by someone else!!
        self.restart_accumulator()
        self.max_accumulate = max_accumulate

    def restart_accumulator(self):
        self.accumulator = []

    def generate(self, timestamp, acc_data):
        """Generator of acc_data."""

        self.accumulator.extend(acc_data)

        if len(self.accumulator) < self.max_accumulate:
            return

        accumulated = np.array(self.accumulator)
        data = [np.mean(accumulated[:, i]) for i in range(3)]
        # 0 is x, 1 is y, 2 is z

        self.restart_accumulator()

        yield from self.generator.generate(timestamp, data)
