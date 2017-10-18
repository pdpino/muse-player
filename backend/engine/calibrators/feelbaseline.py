"""Provide a calibrator to compare with a baseline."""
from scipy.stats import norm
import numpy as np

### DEPRECATED
# class FeelCalculator(Calibrator):
#     """Collect data and calculate feeling from new data comparting with the old data."""
#
#     def __init__(self, arr_freqs, test_population=False, limit_population=10):
#         """Constructor.
#
#         limit_population -- limit the amount of data in each interval"""
#         super().__init__()
#
#         # Calibrate objects # start empty
#         self.baseline_data = None
#         self.baseline_counter = 0
#
#         # Alias for the function
#         self.feel = self.calibrate
#
#         # List of frequencies
#         self.arr_freqs = arr_freqs
#
#         self._limit_population = limit_population
#
#         # What does the class do
#         self._what_does = "collecting"
#
#         self.relax = FeelAccumulator(test_population)
#         self.concentrate = FeelAccumulator(test_population)
#
#     def _return_empty_feel(self):
#         return None
#
#     def _start_calibrating(self, power):
#         # Signal has been received, start variables
#         self.baseline_data = []
#         self.baseline_counter = 0
#
#         # Change status to start calibrating in the next iteration
#         self._set_status_calibrating()
#
#         return self._return_empty_feel()
#
#     def _calibrating(self, power):
#         # Add data to the array
#         self.baseline_data.append(power)
#         self.baseline_counter += 1
#
#         return self._return_empty_feel()
#
#     def _stop_calibrating(self, power):
#         # Average the collected data
#         if self.baseline_counter > 0:
#             # data as array
#             all_data = np.array(self.baseline_data) # shape: (time, n_chs, n_freqs)
#
#             # Flattened data # HACK: channels and waves hardcoded
#             flat_alpha = all_data[:, 0::3, info.get_freqs_filter(self.arr_freqs, 8, 13)].flatten()
#             flat_beta = all_data[:, 1:3, info.get_freqs_filter(self.arr_freqs, 13, 30)].flatten()
#
#             self.relax.add_base(flat_alpha)
#             self.concentrate.add_base(flat_beta)
#
#             self.accumulated = 0
#
#             self._set_status_calibrated()
#         else:
#             print("No data found to collect, try collecting again") # REFACTOR: warn msg
#             self._set_status_non_calibrated()
#
#         return self._return_empty_feel()
#
#     def _non_calibrated(self, power):
#         """Return the raw data."""
#         return self._return_empty_feel()
#
#     def _calibrated(self, power):
#         """Return the data once the calibrating time has passed."""
#         # Get waves # HACK: waves hardcoded
#         alpha = tf.get_wave(power, self.arr_freqs, 8, 13) # alpha has shape: (n_chs, )
#         beta = tf.get_wave(power, self.arr_freqs, 13, 30)
#
#         # grab channels # HACK: channels hardcoded
#         alpha1 = alpha[0] # ear channels
#         alpha2 = alpha[3]
#         beta1 = beta[1] # forehead channels
#         beta2 = beta[2]
#
#         # Accumulate
#         self.relax.accumulate_data(alpha1, alpha2)
#         self.concentrate.accumulate_data(beta1, beta2)
#         self.accumulated += 1
#
#         if self.accumulated > self._limit_population:
#             # Hypothesis test
#             current_relax = self.relax.test()
#             current_concentrate = self.concentrate.test()
#
#             self.relax.reset_data()
#             self.concentrate.reset_data()
#
#             # Restart
#             self.accumulated = 0
#
#             return [current_relax, current_concentrate]
#         else:
#             return self._return_empty_feel()

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
