import numpy as np
from backend import tf, info
from .. import collectors, calibrators, yielders
from . import base

## DEPRECATED:
# class FeelProcessor(base.BaseProcessor):
#     """Provides a feeling processor."""
#
#     def __init__(self):
#
#         # HACK: values hardcoded
#         test_population = False
#         feeling_interval = 1
#         window = 256
#         srate = 256
#         step = 25
#
#         arr_freqs = tf.get_freqs_resolution(window, srate)
#         waves_freq = int(window/step)
#
#         self.feel_calculator = calibrators.FeelCalculator(np.array(arr_freqs),
#                     test_population=test_population,
#                     limit_population=waves_freq * feeling_interval)
#
#         # Collection
#         self.feel_collector = collectors.FeelCollector()
#
#         # Yielding
#         self.generator = yielders.FeelYielder()
#
#     def generate(self, timestamp, power):
#         """Generator of feelings."""
#
#         feeling = self.feel_calculator.feel(power)
#
#         if not feeling is None:
#             self.feel_collector.collect(timestamp, feeling)
#
#             yield self.generator.generate(timestamp, feeling)

class EmptyBaselineHandler:
    def update(self, timestamp, feeling):
        """Don't update anything."""
        return True

    def normalize(self, feeling):
        """Don't normalize, return same feeling."""
        return feeling

## Example for a formula:
# def formula(power):
#     """Transform power into feeling.
#
#     timestamp -- float
#     power -- np.array of shape (n_chs, n_freqs)
#     """
#
#     # REVIEW: use a dict to transform to JSON? depends on formatters to yield
#
#     feeling1 = 0
#     feeling2 = 1
#
#     return [feeling1, feeling2] # could be more than 2


def get_relaxation_concentration(power):
    """Transform power into a relaxation and concnetration status."""

    # HACK: this shouldn't be done every time
    arr_freqs = tf.get_freqs_resolution(256, 256)

    # Alpha for earback channels (TP9 and TP10)
    flat_alpha = power[0::3, info.get_freqs_filter(arr_freqs, 8, 13)].flatten()

    # Beta for forehead channels (AF7 and AF8)
    flat_beta = power[1:3, info.get_freqs_filter(arr_freqs, 13, 30)].flatten()

    # Average for both channels
    relaxation = np.mean(flat_alpha)
    concentration = np.mean(flat_beta)

    return [relaxation, concentration]

class PowerAccumulator:
    """Accumulates power data."""

    def __init__(self):
        """Constructor."""

        # How many samples to accumulate before sending out
        self.samples = 10

        self._reset_cumulator()

    def _reset_cumulator(self):
        self._accumulated = []
        self._cumulator_count = 0

    def accumulate(self, power):
        self._accumulated.append(power)
        self._cumulator_count += 1

        if self._cumulator_count >= self.samples:
            accumulated = np.array(self._accumulated)
            self._reset_cumulator()

            # TODO: provide other options (besides from mean)
            return np.mean(accumulated, axis=0)
        else:
            return None



class FeelProcessor(base.BaseProcessor):
    """Provides a feeling processor."""

    def __init__(self):# , formula):
        """Constructor.

        formula -- function that receives # TODO
        """
        # Baseline handler
        self.baseline_handler = EmptyBaselineHandler() # TODO: use real handler

        # To accumulate data in more than one instant
        self.accumulator = PowerAccumulator()

        # Formula to calculate feeling
        self.formula = get_relaxation_concentration # TODO: provide formula in real time

        # Collection of feelings
        self.collector = collectors.FeelCollector()

        # Yielding
        self.generator = yielders.FeelYielder()

    def generate(self, timestamp, power):
        """Generator of feelings."""

        # Accumulate in time
        effective_power = self.accumulator.accumulate(power)
        if effective_power is None:
            return

        # Apply feeling formula
        raw_feeling = self.formula(effective_power)

        # Update baseline
        baseline_ready = self.baseline_handler.update(timestamp, raw_feeling)
        if not baseline_ready:
            return

        # Normalize by baseline
        feeling = self.baseline_handler.normalize(raw_feeling)

        # Collect processed feeling
        self.collector.collect(timestamp, feeling)

        # Yield it
        yield from self.generator.generate(timestamp, feeling)
