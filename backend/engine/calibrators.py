"""Provide calibrator handlers."""
import threading
from enum import Enum
import numpy as np

class WaveCalibStatus(Enum):
    """Status of the calibration of the wave."""
    No = 0 # There is no calibration
    Start = 1 # A start_calibrating() signal has been received
    Calibrating = 2 # Currently saving baseline
    Stop = 3 # A stop_calibrating() signal has been received
    Yes = 4 # The baseline is already saved and the data is being normalized

class WaveCalibrator(object):
    """Provides functions to calibrate data."""

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
        return 10*np.log10(power/self.calib_arr)

    def _no(self, power):
        return power

    def calibrate(self, power):
        """Public method to call in each iteration, it will be decided what to do with the power matrix according to the status."""
        return self._func_dict[self._get_status()](power)

    def start_calibrating(self):
        """Set start calibrating."""
        self._set_status(WaveCalibStatus.Start)
        return True

    def stop_calibrating(self):
        """Set stop calibrating."""
        if self._get_status() == WaveCalibStatus.Calibrating:
            self._set_status(WaveCalibStatus.Stop)
            return True
        else:
            return False

class WaveDivider(WaveCalibrator):
    """."""

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
        # Use baseline data to normalize
        # power = tf.normalize_power(power, calib_arr)
        return 10*np.log10(power/self.calib_arr)

    def _no(self, power):
        return power
