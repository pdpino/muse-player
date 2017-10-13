from . import base

class WaveDivider(base.Calibrator):
    """Provides calibration dividing data by a baseline period."""

    def __init__(self):
        super().__init__()

        # Calibration objects
        self.baseline = None
        self.counter = 0

    def _start_calibrating(self, power):
        """Start collecting baseline."""
        self.baseline = np.zeros(power.shape)
        self.counter = 0

        # Move to calibrating
        self._set_status_calibrating()

        return power

    def _calibrating(self, power):
        """Collect the data in the baseline."""
        self.baseline += power
        self.counter += 1

        return power

    def _stop_calibrating(self, power):
        """Stop collecting the baseline"""

        if self.counter > 0:
            self.baseline /= self.counter
            self._set_status_calibrated()
        else:
            # REVIEW: error msg
            self._set_status_non_calibrated()

        return power

    def _calibrated(self, power):
        """Return the data divided by baseline."""
        # REFACTOR: use function in tf module
        return 10*np.log10(power/self.baseline)

    def _non_calibrated(self, power):
        return power
