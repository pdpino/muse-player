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

    The calibrator can be in one of 5 status:
        non-calibrated, started-calibrating, calibrating, stopped-calibrating, calibrated
    In time (each iteration of your program) call:
        data = calibrator.calibrate(data)
        which will modify the data according to the current status
    Send signals to the calibrator: start-calibrating and stop-calibrating, to modify the status
    Provide functions to the calibrator to call in each status"""

    def __init__(self, info="calibrating"):
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

    def _set_status(self, new_status):
        """Wrapper to change the status of the calibrator."""
        with self._lock_s:
            self._status = new_status

    def _set_status_calibrating(self):
        self._set_status(self, CalibrationStatus.Calibrating)

    def _set_status_non_calibrated(self):
        self._set_status(self, CalibrationStatus.NonCalibrated)

    def _set_status_calibrated(self):
        self._set_status(self, CalibrationStatus.Calibrated)

    def _get_status(self):
        """Wrapper to get the status."""
        # Obtain status
        with self._lock_s:
            status = self._status
        return status

    def _start_calibrating(self, data):
        return data

    def _calibrating(self, data):
        return data

    def _stop_calibrating(self, data):
        return data

    def _calibrated(self, data):
        return data

    def _non_calibrated(self, data):
        return data

    def is_calibrated(self):
        return self._get_status() == CalibrationStatus.Calibrated

    def calibrate(self, power):
        """Public method to call in each iteration, it will be decided what to do with the power matrix according to the status."""
        return self._functions[self._get_status()](power)

    def start_calibrating(self):
        if self._get_status() == CalibrationStatus.NonCalibrated:
            self._set_status(CalibrationStatus.Start)
            return True
        else:
            # REFACTOR: error msg
            print("Can't start calibrating again")
            return False

    def stop_calibrating(self):
        if self._get_status() == CalibrationStatus.Calibrating:
            self._set_status(CalibrationStatus.Stop)
            return True
        else:
            print("Can't stop {} if you are not {}!".format(self._what_does, self._what_does))
            return False
