import json

class BaseYielder:
    """Base class to create yielders. The yielders are an specific type of Generator

    To call start_message() the instance must have a self.config_data attribute"""

    def __init__(self):
        self.config_data = dict()

    def json_to_string(self, json_dict):
        """Transform a dict of data into a sendable string."""
        return 'data:' + json.dumps(json_dict) + '\n\n'

    def has_start_message(self):
        return True

    def start_message(self):
        return "event: initialize\n" + self.json_to_string(self.config_data)

    def generate(self, timestamp, data):
        """Template method."""
        packed_data = self.pack_data(timestamp, data)
        a = self.json_to_string(packed_data)

        print(a)
        yield a

    def pack_data(self, timestamp, data):
        """Override this method to pack your data into a dict accordingly.

        The method must receive a timestamp and data,
        and must return a json-dumpable object"""
        raise(BaseException("Abstract method to pack the data"))
