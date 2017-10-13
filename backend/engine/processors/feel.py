import numpy as np
from backend import tf
from .. import collectors, calibrators, yielders
from . import base

class FeelProcessor(base.BaseProcessor):
    """Provides a feeling processor."""

    def __init__(self):

        # HACK: values hardcoded
        test_population = False
        feeling_interval = 1
        window = 256
        srate = 256
        step = 25

        arr_freqs = tf.get_freqs_resolution(window, srate)
        waves_freq = int(window/step)

        self.feel_calculator = calibrators.FeelCalculator(np.array(arr_freqs),
                    test_population=test_population,
                    limit_population=waves_freq * feeling_interval)

        # Collection
        self.feel_collector = collectors.FeelCollector()

        # Yielding
        self.generator = yielders.FeelYielder()

    def generate(self, timestamp, power):
        """Generator of feelings."""

        feeling = self.feel_calculator.feel(power)

        if not feeling is None:
            self.feel_collector.collect(timestamp, feeling)

            yield self.generator.generate(timestamp, feeling)
