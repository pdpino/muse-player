import numpy as np
from .. import collectors
from . import base

class EmptyBaselineHandler:
    def update(self, timestamp, feeling):
        """Don't update anything."""
        return True

    def normalize(self, feeling):
        """Don't normalize, return same feeling."""
        return feeling

class FeelProcessor(base.BaseProcessor):
    """Provides a feeling processor."""

    def __init__(self, accum_samples, feeler):
        """Constructor.

        TODO
        """
        # Baseline handler
        self.baseline_handler = EmptyBaselineHandler() # TODO: use real handler

        # To accumulate data in more than one instant
        if accum_samples > 1:
            self.accumulator = collectors.PowerAccumulator()
        else:
            self.accumulator = collectors.NoPowerAccumulator()

        # Feeler, provides formula and yielding
        self.feeler = feeler

        # Different name for the feeler
        self.generator = self.feeler # The generator is the feeler

        # Collection of feelings
        self.collector = collectors.FeelCollector()

    def generate(self, timestamp, power):
        """Generator of feelings."""

        # Accumulate in time
        effective_power = self.accumulator.accumulate(power)
        if effective_power is None:
            return

        # Apply feeling formula
        raw_feeling = self.feeler.calculate(effective_power)

        # Update baseline
        baseline_ready = self.baseline_handler.update(timestamp, raw_feeling)
        if not baseline_ready:
            return

        # Normalize by baseline
        feeling = self.baseline_handler.normalize(raw_feeling)

        # Collect processed feeling
        self.collector.collect(timestamp, feeling)

        # Yield it
        yield from self.feeler.generate(timestamp, feeling)
