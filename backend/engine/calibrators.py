"""Provide calibrator handlers."""
import threading
from enum import Enum
import numpy as np
from scipy.stats import norm
from backend import info, tf

class WaveCalibStatus(Enum):
    """Status of the calibration of the wave."""
    No = 0 # There is no calibration
    Start = 1 # A start_calibrating() signal has been received
    Calibrating = 2 # Currently saving baseline
    Stop = 3 # A stop_calibrating() signal has been received
    Yes = 4 # The baseline is already saved and the data is being normalized

class WaveCalibrator(object):
    """Abstract class to calibrate data."""

    def __init__(self):
        # Functions to call
        self._func_dict = {
            WaveCalibStatus.No: self._no,
            WaveCalibStatus.Start: self._start,
            WaveCalibStatus.Calibrating: self._calibrating,
            WaveCalibStatus.Stop: self._stop,
            WaveCalibStatus.Yes: self._yes
        }

        # Status
        self._lock_s = threading.Lock()
        self._status = WaveCalibStatus.No

        # What do the class do
        self._what_does = "calibrating"

    def _set_status(self, new_status):
        """Wrapper to change the status of the calibrator."""
        with self._lock_s:
            self._status = new_status

    def _get_status(self):
        """Wrapper to get the status."""
        # Obtain status
        with self._lock_s:
            status = self._status
        return status

    def _start(self, power):
        return power

    def _calibrating(self, power):
        return power

    def _stop(self, power):
        return power

    def _yes(self, power):
        return power

    def _no(self, power):
        return power

    def is_calibrated(self):
        return self._get_status() == WaveCalibStatus.Yes

    def calibrate(self, power):
        """Public method to call in each iteration, it will be decided what to do with the power matrix according to the status."""
        return self._func_dict[self._get_status()](power)

    def start_calibrating(self):
        """Set start calibrating."""
        if self._get_status() == WaveCalibStatus.No:
            self._set_status(WaveCalibStatus.Start)
            return True
        else:
            print("Can't start calibrating again") # REFACTOR: error msg
            return False

    def stop_calibrating(self):
        """Set stop calibrating."""
        if self._get_status() == WaveCalibStatus.Calibrating:
            self._set_status(WaveCalibStatus.Stop)
            return True
        else:
            print("Can't stop {} if you are not {}!".format(self._what_does, self._what_does))
            return False

class WaveDivider(WaveCalibrator):
    """Provides calibration dividing data by a baseline period."""

    def __init__(self):
        super().__init__()
        # Calibrate objects # start empty
        self.calib_arr = None
        self.calib_counter = 0

    def _start(self, power):
        # Signal has been received, start variables
        self.calib_arr = np.zeros(power.shape)
        self.calib_counter = 0

        # Change status to start calibrating in the next iteration
        self._set_status(WaveCalibStatus.Calibrating)

        return power

    def _calibrating(self, power):
        # Add data to the array
        self.calib_arr += power
        self.calib_counter += 1

        return power

    def _stop(self, power):
        # Average the collected data
        if self.calib_counter > 0:
            self.calib_arr /= self.calib_counter
            self._set_status(WaveCalibStatus.Yes)
        else:
            self._set_status(WaveCalibStatus.No)

        return power

    def _yes(self, power):
        """Return the data divided by baseline."""
        return 10*np.log10(power/self.calib_arr)

    def _no(self, power):
        return power

class FeelCalculator(WaveCalibrator):
    """Collect data and calculate feeling from new data comparting with the old data."""

    def __init__(self, arr_freqs, test_population=False, limit_population=10):
        """Constructor.

        limit_population -- limit the amount of data in each interval"""
        super().__init__()

        # Calibrate objects # start empty
        self.baseline_data = None
        self.baseline_counter = 0

        # Alias for the function
        self.feel = self.calibrate

        # List of frequencies
        self.arr_freqs = arr_freqs

        self._limit_population = limit_population

        # What does the class do
        self._what_does = "collecting"

        self.relax = FeelAccumulator(test_population)
        self.concentrate = FeelAccumulator(test_population)

    def _return_empty_feel(self):
        return None

    def _start(self, power):
        # Signal has been received, start variables
        self.baseline_data = []
        self.baseline_counter = 0

        # Change status to start calibrating in the next iteration
        self._set_status(WaveCalibStatus.Calibrating)

        return self._return_empty_feel()

    def _calibrating(self, power):
        # Add data to the array
        self.baseline_data.append(power)
        self.baseline_counter += 1

        return self._return_empty_feel()

    def _stop(self, power):
        # Average the collected data
        if self.baseline_counter > 0:
            # data as array
            all_data = np.array(self.baseline_data) # shape: (time, n_chs, n_freqs)

            # Flattened data # HACK: channels and waves hardcoded
            flat_alpha = all_data[:, 0::3, info.get_freqs_filter(self.arr_freqs, 8, 13)].flatten()
            flat_beta = all_data[:, 1:3, info.get_freqs_filter(self.arr_freqs, 13, 30)].flatten()

            self.relax.add_base(flat_alpha)
            self.concentrate.add_base(flat_beta)

            self.accumulated = 0

            self._set_status(WaveCalibStatus.Yes)
        else:
            print("No data found to collect, try collecting again") # REFACTOR: warn msg
            self._set_status(WaveCalibStatus.No)

        return self._return_empty_feel()

    def _no(self, power):
        """Return the raw data."""
        return self._return_empty_feel()

    def _yes(self, power):
        """Return the data once the calibrating time has passed."""
        # Get waves # HACK: waves hardcoded
        alpha = tf.get_wave(power, self.arr_freqs, 8, 13) # alpha has shape: (n_chs, )
        beta = tf.get_wave(power, self.arr_freqs, 13, 30)

        # grab channels # HACK: channels hardcoded
        alpha1 = alpha[0] # ear channels
        alpha2 = alpha[3]
        beta1 = beta[1] # forehead channels
        beta2 = beta[2]

        # Accumulate
        self.relax.accumulate_data(alpha1, alpha2)
        self.concentrate.accumulate_data(beta1, beta2)
        self.accumulated += 1

        if self.accumulated > self._limit_population:
            # Hypothesis test
            current_relax = self.relax.test()
            current_concentrate = self.concentrate.test()

            self.relax.reset_data()
            self.concentrate.reset_data()

            # Restart
            self.accumulated = 0

            return [current_relax, current_concentrate]
        else:
            return self._return_empty_feel()

class FeelAccumulator(object):
    """Accumulates feeling information."""

    def __init__(self, test_population=False):
        self.test = self._test_one if not test_population else self._test_population

        self.reset_data()

    def add_base(self, base_data):
        """Add baseline data for that feeling."""
        # Fit gaussian # for a regular hypothesis test
        self.fit_mu, self.fit_sd = norm.fit(base_data)

        # Save for poblations test
        self.real_mu = np.mean(base_data)
        self.real_var_by_n = np.var(base_data) / len(base_data)

    def accumulate_data(self, *new_data):
        self.accumulated_data.extend([*new_data])
        self.accumulated_counter += 1

    def reset_data(self):
        self.accumulated_data = []
        self.accumulated_counter = 0

    def _test_one(self):
        """Perform an hypothesis test for the new population (self.accumulated_data) vs the collected data."""
        numerator = np.mean(self.accumulated_data) - self.fit_mu
        denominator = self.fit_sd/np.sqrt(self.accumulated_counter)
        statistic = numerator / denominator
        return statistic

    def _test_population(self):
        """Perform a hypothesis test between the new population (self.accumulated_data) and the collected population."""
        acum_var_by_n = np.var(self.accumulated_data) / self.accumulated_counter
        numerator = np.mean(self.accumulated_data) - self.real_mu
        denominator = np.sqrt(self.real_var_by_n + acum_var_by_n)
        statistic = numerator / denominator
        return statistic
