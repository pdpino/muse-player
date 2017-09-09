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
        self.collect_data = None
        self.data_counter = 0

        # Alias for the function
        self.feel = self.calibrate

        # List of frequencies
        self.arr_freqs = arr_freqs

        self._limit_population = limit_population

        # What does the class do
        self._what_does = "collecting"

        # Choose function to test
        self._test = self._test_population if test_population else self._test_one


    def _return_empty_feel(self):
        return None

    def _start(self, power):
        # Signal has been received, start variables
        self.collect_data = []
        self.data_counter = 0

        # Change status to start calibrating in the next iteration
        self._set_status(WaveCalibStatus.Calibrating)

        return self._return_empty_feel()

    def _calibrating(self, power):
        # Add data to the array
        self.collect_data.append(power)
        self.data_counter += 1

        return self._return_empty_feel()

    def _stop(self, power):
        # Average the collected data
        if self.data_counter > 0:
            # data as array
            all_data = np.array(self.collect_data) # shape: (time, n_chs, n_freqs)

            # Flattened data for alpha in one channel # HACK: channel and wave hardcoded
            flat_data = all_data[:, 0, info.get_freqs_filter(self.arr_freqs, 8, 13)].flatten()

            # Fit gaussian
            self.fit_mu, self.fit_sd = norm.fit(flat_data)
            self.real_mu = np.mean(flat_data)
            real_var = np.var(flat_data)
            self.real_var_by_n = real_var / len(flat_data)


            # New queue to accumulate data
            self.accumulated = []

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
        # Get waves
        alpha = tf.get_wave(power, self.arr_freqs, 8, 13) # HACK: alpha wave hardcoded
        # alpha has shape: (n_chs, )

        # grab a channel
        alpha = alpha[0] # HACK: hardcoded

        # Accumulate
        self.accumulated.append(alpha)

        if len(self.accumulated) > self._limit_population:
            # Hypothesis test
            statistic = self._test()

            # Empty list
            self.accumulated = []

            return statistic
        else:
            return self._return_empty_feel()

    def _test_one(self):
        """Perform an hypothesis test for the new population (self.accumulated) vs the collected data."""
        numerator = np.mean(self.accumulated) - self.fit_mu
        denominator = self.fit_sd/np.sqrt(len(self.accumulated))
        return numerator / denominator

    def _test_population(self):
        """Perform a hypothesis test between the new population (self.accumulated) and the collected population."""
        acum_var_by_n = np.var(self.accumulated)/len(self.accumulated)
        numerator = np.mean(self.accumulated) - self.real_mu
        denominator = np.sqrt(self.real_var_by_n + acum_var_by_n)
        return numerator / denominator
