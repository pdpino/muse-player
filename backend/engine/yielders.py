### DEPRECATED !!!
"""Module that provides classes to handle the connections."""
from backend import tf, info
import basic

class WaveYielder(object):
    """Yield the waves to the client."""

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

        for w, min_freq, max_freq in info.iter_waves():
            wave = tf.get_wave(power, self.arr_freqs, min_freq, max_freq)[self.channel]
            all_waves.append(wave)

        # Yield
        yield self.str_format.format(t, *all_waves)
