import numpy as np

class NoPowerAccumulator:
    """Behaves as a PowerAccumulator, but doesn't accumulate."""
    def accumulate(self, power):
        return power

class PowerAccumulator:
    """Accumulates power data."""

    def __init__(self, samples=10):
        """Constructor."""

        # How many samples to accumulate before sending out
        self.samples = samples

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
