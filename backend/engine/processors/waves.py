from backend import tf
from .. import calibrators, yielders
from . import base

class WaveProcessor(base.BaseProcessor):
    """Process the EEG transforming it into waves."""

    def __init__(self, generator):
        # Calibrator
        self.calibrator = calibrators.WaveDivider()

        self.generator = generator

    def generate(self, t_init, timestamp, new_data):
        """Make a TF analysis of the data and delegates to a processor."""
        # Apply fft
        power = tf.apply_fft(new_data) # shape: (n_chs, n_freqs)

        # Calibrate
        power = self.calibrator.calibrate(power)

        # Normalize time
        t_normalized = timestamp - t_init

        yield from self.generator.generate(t_normalized, power)
