from . import base

class AccYielder(base.BaseYielder):
    """Yield the accelerometer data"""

    def __init__(self):
        """Constructor."""
        self.config_data = {} # just in case

    def pack_data(self, timestamp, new_data):
        """Pack the accelerometer data."""
        yield {
            'x': new_data[0],
            'y': new_data[1],
            'z': new_data[2]
        }

    def pack_timestamp(self, timestamp, packed_data):
        pass
        # Don't pack timestamp!
