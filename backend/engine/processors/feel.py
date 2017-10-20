import numpy as np
from .. import collectors
from . import base

class FeelProcessor(base.BaseProcessor):
    """Provides a feeling processor.

    TODO
    """

    def __init__(self, feeler, regulator, feeling_names):
        """Constructor."""

        # Regulator
        self.regulator = regulator

        # Feeler, provides formula and yielding
        self.feeler = feeler

        # Different name for the feeler, so the BaseProcessor can use it
        self.generator = self.feeler # The generator is the feeler

        # Collection of feelings
        self.collector = collectors.FeelCollector(feeling_names)
        self.export = self.collector.export # HACK: this shouldnt be done this way

    def generate(self, timestamp, power):
        """Generator of feelings."""

        # Apply feeling formula
        feeling = self.feeler.calculate(power)

        # Regulate with baseline and/or accumulation
        if self.regulator:
            feeling = self.regulator.regulate(feeling)
            if feeling is None:
                return

        # Collect processed feeling
        self.collector.collect(timestamp, feeling)

        # Yield it
        yield from self.feeler.generate(timestamp, feeling)
