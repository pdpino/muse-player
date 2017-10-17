import numpy as np
from .. import collectors, calibrators
from . import base

class FeelProcessor(base.BaseProcessor):
    """Provides a feeling processor.

    TODO"""

    def __init__(self, feeler):
        """Constructor."""

        # Calibrator
        # TODO: select from outside
        # self.calibrator = calibrators.Calibrator(calibrators.BaselineFeeling())
        self.calibrator = calibrators.NoCalibrator()

        # Feeler, provides formula and yielding
        self.feeler = feeler

        # Different name for the feeler
        self.generator = self.feeler # The generator is the feeler

        # Collection of feelings
        self.collector = collectors.FeelCollector()

    def generate(self, timestamp, power):
        """Generator of feelings."""

        # Apply feeling formula
        raw_feeling = self.feeler.calculate(power)

        # Normalize by baseline
        feeling = self.calibrator.calibrate(raw_feeling)
        if feeling is None:
            return

        # Collect processed feeling
        self.collector.collect(timestamp, feeling)

        # Yield it
        yield from self.feeler.generate(timestamp, feeling)
