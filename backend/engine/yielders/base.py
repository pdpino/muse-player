import json

class BaseYielder:
    """Base class to create yielders. The yielders are an specific type of Generator

    To call start_message() the instance must have a self.config_data attribute"""

    def __init__(self):
        self.config_data = dict()

    def data_to_string(self, data):
        """Transform sendable data into a sendable string."""
        return "data:" + json.dumps(data) + "\n\n"

    def start_message(self):
        return "event: initialize\n" + self.data_to_string(self.config_data)

    def generate(self, timestamp, data):
        """Provide a template to generate data.

        First pack the data (can be one or many packages)
        Then pack the timestamp (the specific class can choose a way to do this, or not do this)
        Finally yield it"""
        for packed_data in self.pack_data(timestamp, data):
            self.pack_timestamp(timestamp, packed_data)
            yield self.data_to_string(packed_data)

    def pack_timestamp(self, timestamp, packed_data):
        """Append timestamp to a package of data.

        This method can be overriden by a dummy method to not pack the timestamp on the data
        If you pack the timestamp in other place (not this method), be sure to follow the format"""
        packed_data.append({
            "name": "timestamp",
            "value": timestamp,
            # "color": "black" # HACK: needed for moodplay?
            # isn't needed for muse-player web client
        })

    def pack_data(self, timestamp, data):
        """Override this method to pack your data into a dict accordingly. Must be a generator

        The method must receive a timestamp and data,
        and must yield a json-dumpable object (or multiple).
        Don't include the timestamp in the object returned, its included later by generate method (the timestamp is passed in case is needed by pack_data())

        Use yield None or return (only when catching specific case) if nothing has to be yielded in that step"""
        raise(BaseException("Abstract method to pack the data"))
