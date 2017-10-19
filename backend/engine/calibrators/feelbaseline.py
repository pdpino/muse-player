"""Provide a calibrator to compare with a baseline."""
from scipy.stats import norm
import numpy as np

### DEPRECATED: population tests
# def add_base(self, base_data):
#     """Add baseline data for that feeling."""
#     # Save for poblations test
#     self.real_mu = np.mean(base_data)
#     self.real_var_by_n = np.var(base_data) / len(base_data)
#
# def _test_population(self):
#     """Perform a hypothesis test between the new population (self.accumulated_data) and the collected population."""
#     acum_var_by_n = np.var(self.accumulated_data) / self.accumulated_counter
#     numerator = np.mean(self.accumulated_data) - self.real_mu
#     denominator = np.sqrt(self.real_var_by_n + acum_var_by_n)
#     statistic = numerator / denominator
#     return statistic

class BaselineFeeling:
    """Implements IBaselineHandler.

    TODO
    returns None because feel is not ready"""

    def __init__(self, baseline_limit=10, accumulator_limit=1):
        """."""
        self.baseline_limit = baseline_limit

        self.accumulator_limit = accumulator_limit

        self._reset_baseline()
        self._reset_accumulator()

    def _reset_baseline(self):
        self.baseline_data = []
        self.baseline_counter = 0

    def _reset_accumulator(self):
        # HACK:
        # should this be in another object ?? design it better!
        self.accumulator_data = []
        self.accumulator_counter = 0

    def start_calibrating(self, feeling):
        """Signal has been received, start variables."""
        self._reset_baseline()

        return None

    def calibrating(self, feeling):
        # Add data to the array
        self.baseline_data.append(feeling)
        self.baseline_counter += 1

        stop_calibrating = self.baseline_counter >= self.baseline_limit

        return None, stop_calibrating

    def stop_calibrating(self, feeling):
        if self.baseline_counter > 0:
            # data as array, shape: (time, n_feelings)
            baseline_data = np.array(self.baseline_data)

            n_times, self.n_feelings = baseline_data.shape

            # Save baseline gaussian data
            self.fit_mu = []
            self.fit_sd = []
            for i_feel in range(self.n_feelings):
                fit_mu, fit_sd = norm.fit(baseline_data[:, i_feel])

                self.fit_mu.append(fit_mu)
                self.fit_sd.append(fit_sd)

            # Start accumulator
            self._reset_accumulator()

            is_ok = True
        else:
            self._reset_baseline() # Just in case
            is_ok = False

        return None, is_ok

    def non_calibrated(self, data):
        return None

    def calibrated(self, feeling):
        self.accumulator_data.append(feeling)
        self.accumulator_counter += 1

        if self.accumulator_counter >= self.accumulator_limit:
            statistics = []

            accumulated_feelings = np.array(self.accumulator_data)

            for i_feel in range(self.n_feelings):
                # Mean of the accumulated data
                feeling = np.mean(accumulated_feelings[:, i_feel])

                # Calculate statistic
                numerator = feeling - self.fit_mu[i_feel]
                denominator = self.fit_sd[i_feel] / np.sqrt(self.baseline_counter)

                # statistics of all the feelings saved
                statistics.append(numerator / denominator)

                # REVIEW: Is the test correctly applied?

            self._reset_accumulator()

            return statistics
        else:
            return None
