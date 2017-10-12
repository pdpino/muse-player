import basic

class EEGRawYielder:
    """Process raw eeg data and yields it in a specified way

    Assumes that the shape of the data is:
    len(timestamp) == 12
    data.shape == (5, 12)"""

    def __init__(self, mode, args=None):
        ## REFACTOR: use formatter instead
        # String para hacer yield
        # EEG envia (timestamp, ch0, ch1, ch2, ch3, ch4)
        self.yield_string = "data: {}, {}, {}, {}, {}, {}\n\n"

        self.args = args

        # Select yielder
        yielders = {
            "mean": self._get_data_mean,
            "min": self._get_data_min,
            "max": self._get_data_max,
            "n": self._get_data_n
            }
        try:
            self._yielder = yielders[mode]
        except KeyError:
            basic.perror("yielder: {} not found".format(mode), force_continue=True)
            self._yielder = self._get_data_n # DEFAULT value

    def _get_data_mean(self, t_init, timestamp, data, dummy=None):
        """Yield the mean in the 12 samples for each channel separately."""
        yield self.yield_string.format( \
                timestamp.mean() - t_init, \
                data[0].mean(), \
                data[1].mean(), \
                data[2].mean(), \
                data[3].mean(), \
                data[4].mean() )

    def _get_data_max(self, t_init, timestamp, data, dummy=None):
        """Yield the max of the 12 samples for each channel separately"""
        # NOTE: use timestamp.max(), timestamp.mean()?
        yield self.yield_string.format( \
                timestamp.max() - t_init, \
                data[0].max(), \
                data[1].max(), \
                data[2].max(), \
                data[3].max(), \
                data[4].max() )

    def _get_data_min(self, t_init, timestamp, data, dummy=None):
        """Yield the min of the 12 samples for each channel separately"""
        yield self.yield_string.format( \
                timestamp.min() - t_init, \
                data[0].min(), \
                data[1].min(), \
                data[2].min(), \
                data[3].min(), \
                data[4].min() )

    def _get_data_n(self, t_init, timestamp, data, n):
        """Yield n out of the 12 samples."""
        for i in range(n):
            tt = timestamp[i] - t_init
            yield self.yield_string.format(
                tt, \
                data[0][i], \
                data[1][i], \
                data[2][i], \
                data[3][i], \
                data[4][i] )

    def process(self, t_init, timestamp, new_data):
        """Process new eeg data."""
        yield from self._yielder(t_init, timestamp, new_data, *self.args)
