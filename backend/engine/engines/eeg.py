from time import sleep

class EEGEngine:
    """Engine to handle the receiving of EEG and streaming different kinds of data, according to its processor."""

    def __init__(self, name, eeg_collector, eeg_buffer, generator):
        """Initialize.

        name -- string identifier
        eeg_collector -- implements interface ICollector
        eeg_buffer -- implements interface IBuffer
        generator -- implements interface IGenerator"""

        self.name = name or "Muse Player"
        self.eeg_collector = eeg_collector
        self.eeg_buffer = eeg_buffer
        self.generator = generator

    def incoming_data(self, timestamps, new_data):
        """Proccess the incoming data."""
        self.eeg_collector.collect(timestamps, new_data)

        self.eeg_buffer.incoming(timestamps, new_data)

    def outgoing_data(self):
        """Generator that yields the outgoing data."""

        yield self.generator.start_message()

        # Mark initial time
        t_init = self.eeg_buffer.peek_last_time()

        self.eeg_buffer.clear()

        while True:
            timestamp, new_data = self.eeg_buffer.outgoing()

            if timestamp is None or new_data is None:
                sleep(0.1)
                continue

            normalized_timestamp = timestamp - t_init

            yield from self.generator.generate(normalized_timestamp, new_data)
