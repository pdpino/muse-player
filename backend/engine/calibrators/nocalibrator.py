class NoCalibrator:
    """Empty calibrator (does nothing)."""

    def calibrate(self, data):
        return data

    def is_calibrated(self):
        return True
