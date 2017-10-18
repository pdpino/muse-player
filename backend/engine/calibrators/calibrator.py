import threading
from enum import Enum

class CalibrationStatus(Enum):
    """Status of the calibration."""
    NonCalibrated = 0 # There is no calibration
    Start = 1 # A start_calibrating() signal has been received
    Calibrating = 2 # Currently calibrating
    Stop = 3 # A stop_calibrating() signal has been received
    Calibrated = 4 #

class Calibrator:
    """Provides an object that can calibrate data in time.

    Implements IRegulator

    The calibrator can be in one of 5 status:
        non-calibrated, started-calibrating, calibrating, stopped-calibrating, calibrated
    In each iteration of your program call:
        `data = calibrator.calibrate(data)`
        which will modify the data according to the current status
    Send signals to the calibrator: start-calibrating and stop-calibrating, to modify the status
    You must provide a IBaselineHandler object (TODO)"""

    def __init__(self, baseline_handler, info="calibrating"):
        self._functions = {
            CalibrationStatus.NonCalibrated: self._non_calibrated,
            CalibrationStatus.Start: self._start_calibrating,
            CalibrationStatus.Calibrating: self._calibrating,
            CalibrationStatus.Stop: self._stop_calibrating,
            CalibrationStatus.Calibrated: self._calibrated
        }

        # Status
        self._lock_s = threading.Lock()
        self._status = CalibrationStatus.NonCalibrated

        # What do the class do
        self.info = info

        # Baseline handler
        self.baseline_handler = baseline_handler

        # Implement regulator interface
        self.regulate = self.calibrate

    def _set_status(self, new_status):
        """Wrapper to change the status of the calibrator."""
        with self._lock_s:
            self._status = new_status

    def _set_status_calibrating(self):
        self._set_status(self, CalibrationStatus.Calibrating)

    def _set_status_non_calibrated(self):
        self._set_status(self, CalibrationStatus.NonCalibrated)

    def _set_status_stop_calibrating(self):
        self._set_status(self, CalibrationStatus.Stop)

    def _set_status_calibrated(self):
        self._set_status(self, CalibrationStatus.Calibrated)

    def _get_status(self):
        """Wrapper to get the status."""
        # Obtain status
        with self._lock_s:
            status = self._status
        return status

    def _start_calibrating(self, data):
        # Move to calibrating
        self._set_status_calibrating()

        return self.baseline_handler.start_calibrating(data)

    def _calibrating(self, data):
        calibrated_data, stop_calibrating = self.baseline_handler.calibrating(data)

        if stop_calibrating:
            self._set_status_stop_calibrating()

        return calibrated_data

    def _stop_calibrating(self, data):
        calibrated_data, is_ok = self.baseline_handler.stop_calibrating(data)

        if is_ok:
            self._set_status_calibrated()
            return calibrated_data
        else:
            # REVIEW: error msg
            self._set_status_non_calibrated()
            return None

    def _calibrated(self, data):
        return self.baseline_handler.calibrated(data)

    def _non_calibrated(self, data):
        return self.baseline_handler.non_calibrated(data)

    def calibrate(self, data):
        """Public method to call in each iteration, it will be decided what to do with the data according to the status."""
        # TODO: when changing the status change the used function, instead of calculating hash every time
        return self._functions[self._get_status()](data)

    def is_calibrated(self):
        return self._get_status() == CalibrationStatus.Calibrated
