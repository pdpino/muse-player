import numpy as np

class DataAccumulator:
    """Accumulates data (power, feeling, etc)."""

    def __init__(self, samples=10):
        """Constructor."""

        # How many samples to accumulate before sending out
        self.samples = samples

        if samples > 1:
            self._accumulate_function = self._accumulate
        else:
            self._accumulate_function = self._dont_accumulate

        self._reset_cumulator()

    def _reset_cumulator(self):
        self._accumulated = []
        self._cumulator_count = 0

    def _accumulate(self, data):
        self._accumulated.append(data)
        self._cumulator_count += 1

        if self._cumulator_count >= self.samples:
            self.accumulated_data = np.array(self._accumulated)
            self._reset_cumulator()

            # TODO: provide other options (besides from mean)
            return np.mean(self.accumulated_data, axis=0)
        else:
            return None

    def _dont_accumulate(self, data):
        # Copy the data
        self.accumulated_data = np.array(data)

        return data

    def accumulate(self, data):
        """data must be a np.array (of any shape) (if actually something is being accumulated)."""
        return self._accumulate_function(data)
