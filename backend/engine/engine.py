from time import time
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
        self.export = self.eeg_collector.export

        self.eeg_buffer = eeg_buffer

        self.generator = generator

    ## FUTURE:
    # def send_signal_calibrator(sent_signal):
    #     """Send a signal to the calibrator. Return the status of the proccessing of the signal."""
    #     if self.calibrator:
    #         return self.calibrator.signal(sent_signal)
    # def send_signal_collector(sent_signal):
    #     """Send a signal to the collector. Return the status of the proccessing of the signal."""
    #     if self.collector:
    #         return self.collector.signal(sent_signal)

    def incoming_data(self, timestamps, new_data):
        """Proccess the incoming data."""
        self.eeg_collector.collect(timestamps, new_data)

        self.eeg_buffer.incoming(timestamps, new_data)

    def outgoing_data(self):
        """Generator that yields the outgoing data."""

        if self.generator.has_start_message():
            yield self.generator.start_message()

        self.eeg_buffer.clear()

        # Set an initial time as marker
        t_init = time()

        while True:
            timestamp, new_data = self.eeg_buffer.outgoing()

            if timestamp is None or new_data is None:
                continue

            yield from self.generator.generate(t_init, timestamp, new_data)
