"""Module that provides classes to handle the connections."""
import basic

class DataYielder(object):
    """Yield functions to stream any data in the desired way."""

    yield_string = "data: {}, {}\n\n"

    @staticmethod
    def get_data(t, t_init, data, dummy=None):
        """Yield out all the points in the data."""
        data_str = ','.join(map(str, data))
        a = DataYielder.yield_string.format(t - t_init, data_str)
        yield a

class EEGYielder(object):
    """Yield functions to stream the eeg data in the desired way.

    Assumes that the shape of the data is:
    len(t) == 12
    d.shape == (5, 12)"""

    # String para hacer yield
    # EEG envia (timestamp, ch0, ch1, ch2, ch3, ch4)
    yield_string = "data: {}, {}, {}, {}, {}, {}\n\n"

    @staticmethod
    def _get_data_mean(t, t_init, data, dummy=None):
        """Yield the mean in the 12 samples for each channel separately."""
        yield EEGYielder.yield_string.format( \
                t.mean() - t_init, \
                data[0].mean(), \
                data[1].mean(), \
                data[2].mean(), \
                data[3].mean(), \
                data[4].mean() )

    @staticmethod
    def _get_data_max(t, t_init, data, dummy=None):
        """Yield the max of the 12 samples for each channel separately"""
        # NOTE: use tt.max(), tt.mean()?
        yield EEGYielder.yield_string.format( \
                t.max() - t_init, \
                data[0].max(), \
                data[1].max(), \
                data[2].max(), \
                data[3].max(), \
                data[4].max() )

    @staticmethod
    def _get_data_min(t, t_init, data, dummy=None):
        """Yield the min of the 12 samples for each channel separately"""
        yield EEGYielder.yield_string.format( \
                t.min() - t_init, \
                data[0].min(), \
                data[1].min(), \
                data[2].min(), \
                data[3].min(), \
                data[4].min() )

    @staticmethod
    def _get_data_n(t, t_init, data, n):
        """Yield n out of the 12 samples."""
        for i in range(n):
            tt = t[i] - t_init
            yield EEGYielder.yield_string.format(
                tt, \
                data[0][i], \
                data[1][i], \
                data[2][i], \
                data[3][i], \
                data[4][i] )

    @staticmethod
    def get_yielder(mode):
        """Return the selected yielder function"""
        # Available yielders
        yielders = {
            "mean": EEGYielder._get_data_mean,
            "min": EEGYielder._get_data_min,
            "max": EEGYielder._get_data_max,
            "n": EEGYielder._get_data_n
            }

        try:
            yielder = yielders[mode]
        except KeyError:
            basic.perror("yielder: {} not found".format(mode), force_continue=True)
            yielder = EEGYielder._get_data_n # Default

        return yielder
