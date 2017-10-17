class WaveDivider:
    """Implements IBaselineHandler.

    TODO
    """

    def __init__(self):
        # Empty calibration objects
        self.baseline = None
        self.counter = 0

    def non_calibrated(self, power):
        return power

    def start_calibrating(self, power):
        """Start collecting power baseline."""
        self.baseline = np.zeros(power.shape)
        self.counter = 0

        return power

    def calibrating(self, power):
        """Collect the data in the baseline."""
        self.baseline += power
        self.counter += 1

        stop_calibrating = False # Stop only when the signal is sent

        return power, stop_calibrating

    def stop_calibrating(self, power):
        """Stop collecting the baseline"""
        is_ok = False
        if self.counter > 0:
            is_ok = True
            self.baseline /= self.counter

        return power, is_ok

    def calibrated(self, power):
        """Return the data divided by the baseline."""
        # REFACTOR: use function in tf module
        return 10*np.log10(power/self.baseline)
