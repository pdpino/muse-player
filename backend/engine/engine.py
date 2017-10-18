from time import sleep
from . import collectors, buffers, processors

class EEGEngine:
    """Engine to handle the receiving of EEG and streaming different kinds of data, according to its processor."""

    def __init__(self, name, eeg_buffer, generator):
        """Initialize.

        name -- string identifier
        buffer -- implements interface IBuffer
        generator -- implements interface IGenerator"""
        # TODO: do interfaces (abstract classes)

        self.name = name

        self.eeg_collector = collectors.EEGCollector()

        # REVIEW: use property getter?
        self.get_running_time = self.eeg_collector.get_running_time
        self.get_last_timestamp = self.eeg_collector.get_last_timestamp
        self.export = self.eeg_collector.export

        self.eeg_buffer = eeg_buffer

        self.generator = generator

    def incoming_data(self, timestamps, new_data):
        """Proccess the incoming data."""
        self.eeg_collector.collect(timestamps, new_data)

        self.eeg_buffer.incoming(timestamps, new_data)

    def outgoing_data(self):
        """Generator that yields the outgoing data."""

        if self.generator.has_start_message():
            yield self.generator.start_message()

        # Mark initial time
        t_init = self.eeg_buffer.peek_last_time()

        self.eeg_buffer.clear()

        while True:
            timestamp, new_data = self.eeg_buffer.outgoing()

            if timestamp is None or new_data is None:
                sleep(0.1)
                continue

            yield from self.generator.generate(t_init, timestamp, new_data)