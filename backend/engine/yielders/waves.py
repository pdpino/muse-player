from backend import tf, info
from . import base

class WaveYielder(base.BaseYielder):
    """Yield the waves to the client.

    TODO: be able to yield multiple channels (alpha-TP9, beta-TP10, etc), mean of channels, max of channels, etc
    """

    def __init__(self, arr_freqs, channel=0, waves=None):
        """Constructor.

        arr_freqs -- array of frequencies to order the fft
        channel -- select one channel to send the waves
        """
        # Select waves # DEFAULT to all std waves
        self.waves_names = info.get_waves_names(waves or ['delta', 'theta', 'alpha', 'beta', 'gamma'])

        self.config_data = {
            'categories': [{
                'name': wave_name,
                'color': info.get_wave_color(wave_name)
            } for wave_name in self.waves_names ],
            'yAxisLabel': 'Power (dB)',
            'title': 'Waves'
        }

        self.arr_freqs = arr_freqs
        self.channel = channel

    def pack_data(self, timestamp, power):
        """Pack the waves data."""
        yield [{
            'name': wave_name,
            'value': tf.get_wave(power, self.arr_freqs, min_freq, max_freq)[self.channel]
        } for wave_name, min_freq, max_freq in info.iter_waves(self.waves_names)]
