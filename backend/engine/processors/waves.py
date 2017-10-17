from backend import tf
from .. import calibrators, collectors
from . import base

class WaveProcessor(base.BaseProcessor):
    """Process the EEG transforming it into waves.

    TODO"""

    def __init__(self, generator, accum_samples=1):
        """Constructor."""
        # Calibrator uses a wave divider to do the calculation
        self.calibrator = calibrators.Calibrator(calibrators.WaveDivider())

        # To accumulate data in more than one instant
        self.accumulator = collectors.DataAccumulator(samples=accum_samples)

        self.generator = generator

    def generate(self, t_init, timestamp, new_data):
        """Make a TF analysis of the data and delegates to a processor."""
        # Apply fft
        power = tf.apply_fft(new_data) # shape: (n_chs, n_freqs)

        # Calibrate dividing by a baseline
        power = self.calibrator.calibrate(power)

        # Accumulate in time
        effective_power = self.accumulator.accumulate(power)
        if effective_power is None:
            return

        # Normalize time
        t_normalized = timestamp - t_init

        yield from self.generator.generate(t_normalized, effective_power)
