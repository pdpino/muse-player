from backend import tf, info
from . import base

class WaveYielder(base.BaseYielder):
    """Yield the waves to the client."""

    # TODO: be able to yield one channel, mean of channels, max of channels, etc

    def __init__(self, arr_freqs, channel=0, waves=None):
        self.config_data = "waves"

        # Array of frequencies to order the fft
        self.arr_freqs = arr_freqs

        # Select channel to yield
        self.channel = channel

        # Waves
        waves = waves or ['delta', 'theta', 'alpha', 'beta', 'gamma'] # DEFAULT to all std waves
        self.waves_names = info.get_waves_names(waves)

        # String to yield
        self.str_format = "data: {}" # One more for the time
        self.n_waves = len(self.waves_names)
        for i in range(self.n_waves):
            self.str_format += ", {}"
        self.str_format += "\n\n"

    def generate(self, t, power):
        all_waves = []

        # REFACTOR: change name of function, follow standard across yielders

        for w, min_freq, max_freq in info.iter_waves():
            wave = tf.get_wave(power, self.arr_freqs, min_freq, max_freq)[self.channel]
            all_waves.append(wave)

        # Yield
        yield self.str_format.format(t, *all_waves)
