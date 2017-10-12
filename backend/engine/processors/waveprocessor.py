from backend import tf, info
from . import calibrators

class WaveYielder:
    """Yield the waves to the client."""

    # TODO: be able to yield one channel, mean of channels, max of channels, etc

    def __init__(self, arr_freqs, channel=0):
        # Array of frequencies to order the fft
        self.arr_freqs = arr_freqs

        # Select channel to yield
        self.channel = channel

        # Waves
        self.waves_names = info.get_waves_names(['delta', 'theta', 'alpha', 'beta', 'gamma']) # HACK: waves hardcoded

        # String to yield
        self.str_format = "data: {}" # One more for the time
        self.n_waves = len(self.waves_names)
        for i in range(self.n_waves):
            self.str_format += ", {}"
        self.str_format += "\n\n"

    def yield_function(self, t, power):
        all_waves = []

        # REFACTOR: change name of function, follow standard across yielders

        for w, min_freq, max_freq in info.iter_waves():
            wave = tf.get_wave(power, self.arr_freqs, min_freq, max_freq)[self.channel]
            all_waves.append(wave)

        # Yield
        yield self.str_format.format(t, *all_waves)


class WaveProcessor:
    """Process the EEG transforming it into waves."""

    def __init__(self):
        # Calibrator
        self.calibrator = calibrators.WaveDivider()

        # Yielder
        # HACK: window, srate and channel hardcoded
        window = 256
        srate = 256
        channel = 0
        arr_freqs = tf.get_freqs_resolution(window, srate)
        self._yielder = WaveYielder(arr_freqs, channel=channel)

    def process(self, t_init, timestamp, new_data):
        """Make a TF analysis of the data."""
        # Apply fft
        power = tf.apply_fft(new_data) # shape: (n_chs, n_freqs)

        # Calibrate
        power = self.calibrator.calibrate(power)

        # Normalize time
        t_normalized = timestamp - t_init

        # REVIEW: here _yielder is an object, in RawEEGYielder yielder is a generator
        yield from self._yielder.yield_function(t_normalized, power)
