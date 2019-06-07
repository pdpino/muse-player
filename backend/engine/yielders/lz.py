from . import base

class LZYielder(base.BaseYielder):
    """Yield the LZ values."""

    def __init__(self):
        """Constructor."""
        self.config_data = {
            'categories': [{ # HACK: Categories copied from yielders/eeg
                'name': 'TP9-lz',
                'color': 'black',
            }, {
                'name': 'AF7-lz',
                'color': 'red',
            }, {
                'name': 'AF8-lz',
                'color': 'blue',
            }, {
                'name': 'TP10-lz',
                'color': 'green',
            }],
            'yAxisLabel': 'LZ',
            'title': 'LZ',
            'yAutoUpdate': False,
            'yMin': 0,
            'yMax': 1,
        }

    def pack_data(self, timestamp, lzs):
        """Pack the waves data."""
        # HACK: channel names hardcoded
        tp9, af7, af8, tp10 = lzs

        yield [{
            'name': 'TP9-lz',
            'value': tp9
        }, {
            'name': 'AF7-lz',
            'value': af7
        }, {
            'name': 'AF8-lz',
            'value': af8
        }, {
            'name': 'TP10-lz',
            'value': tp10
        }]
