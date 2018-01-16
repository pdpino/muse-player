import basic
from . import base

class EEGRawYielder(base.BaseYielder):
    """Process raw eeg data and yields it in a specified way

    Assumes that the shape of the data is:
    len(timestamp) == 12
    data.shape == (5, 12)


    pack_data() method is overriden in the constructor"""

    def __init__(self, mode, **kwargs):
        self.config_data = {
            'categories': [{
                'name': 'TP9',
                'color': 'black'
            }, {
                'name': 'AF7',
                'color': 'red'
            }, {
                'name': 'AF8',
                'color': 'blue'
            }, {
                'name': 'TP10',
                'color': 'green'
            }, {
                'name': 'Right-Aux',
                'color': 'cyan'
            }],
            'yAxisLabel': 'Raw signal (mV)',
            'title': 'EEG Electrodes'
        }

        self.stream_n = kwargs.get("stream_n") or 12 # DEFAULT hardcoded

        # Select packer
        packers = {
            "mean": self._get_data_mean,
            "min": self._get_data_min,
            "max": self._get_data_max,
            "n": self._get_data_n
            }
        try:
            self.pack_data = packers[mode]
        except KeyError:
            basic.perror("packer: {} not found".format(mode), force_continue=True)
            self.pack_data = self._get_data_n # DEFAULT value

    def _base_packer(self, timestamp, tp9, af7, af8, tp10, right_aux):
        """Return the channels packed in a standard way"""
        return [{
            'name': 'timestamp',
            'value': timestamp
        }, {
            'name': 'TP9',
            'value': tp9
        }, {
            'name': 'AF7',
            'value': af7
        }, {
            'name': 'AF8',
            'value': af8
        }, {
            'name': 'TP10',
            'value': tp10
        }, {
            'name': 'Right-Aux',
            'value': right_aux
        }]

    def _get_data_mean(self, timestamp, data):
        """Yield the mean in the 12 samples for each channel separately."""
        yield self._base_packer(timestamp.mean(), \
                data[0].mean(), \
                data[1].mean(), \
                data[2].mean(), \
                data[3].mean(), \
                data[4].mean())

    def _get_data_max(self, timestamp, data):
        """Yield the max of the 12 samples for each channel separately"""
        # REVIEW: use timestamp.max(), timestamp.mean()?
        yield self._base_packer(timestamp.max(), \
                data[0].max(), \
                data[1].max(), \
                data[2].max(), \
                data[3].max(), \
                data[4].max() )

    def _get_data_min(self, timestamp, data):
        """Yield the min of the 12 samples for each channel separately"""
        yield self._base_packer(timestamp.min(), \
                data[0].min(), \
                data[1].min(), \
                data[2].min(), \
                data[3].min(), \
                data[4].min() )

    def _get_data_n(self, timestamp, data):
        """Yield n out of the 12 samples."""
        for i in range(self.stream_n):
            yield self._base_packer(timestamp[i], \
                data[0][i], \
                data[1][i], \
                data[2][i], \
                data[3][i], \
                data[4][i] )

    def pack_timestamp(self, timestamp, packed_data):
        """The timestamp packing is handled by the pack_data method (in this case, the selected packer)."""
        pass
