import numpy as np
from .. import collectors, calibrators
from . import base

class FeelProcessor(base.BaseProcessor):
    """Provides a feeling processor."""

    def __init__(self, feeler, accum_samples=1):
        """Constructor."""

        # Baseline handler
        self.baseline_handler = calibrators.EmptyBaselineHandler() # TODO: use real handler

        # To accumulate data in more than one instant
        self.accumulator = collectors.DataAccumulator(samples=accum_samples)

        # Feeler, provides formula and yielding
        self.feeler = feeler

        # Different name for the feeler
        self.generator = self.feeler # The generator is the feeler

        # Collection of feelings
        self.collector = collectors.FeelCollector()

    def generate(self, timestamp, power):
        """Generator of feelings."""

        # Apply feeling formula
        feeling = self.feeler.calculate(power)

        # Accumulate in time
        effective_feeling = self.accumulator.accumulate(feeling)
        if effective_feeling is None:
            return

        # REVIEW: calibrator could use accumulator.accumulated_data to correct

        # Normalize by baseline
        normalized_feeling = self.calibrator.calibrate(effective_feeling)
        if normalized_feeling is None:
            return

        # Collect processed feeling
        self.collector.collect(timestamp, normalized_feeling)

        # Yield it
        yield from self.feeler.generate(timestamp, normalized_feeling)
