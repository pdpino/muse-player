from time import time
from . import eegcollector, buffers, processors

class EEGEngine:
    """."""

    def __init__(self, name, processor_args):
        """Initialize."""
        self.name = name
        self.start_msg = "event: config\ndata: eeg\n\n"
        # "event: config\ndata: waves\n\n"

        self.eeg_collector = eegcollector.EEGCollector()
        self.get_running_time = self.eeg_collector.get_running_time # REVIEW: use property getter?
        self.generate_eeg_df = self.eeg_collector.generate_eeg_df

        self.eeg_buffer = buffers.EEGBuffer()

        self.processor = processors.EEGRawYielder("n", args=processor_args)

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

        if self.start_msg:
            yield self.start_msg

        self.eeg_buffer.clear()

        # Set an initial time as marker
        t_init = time()

        while True:
            timestamp, new_data = self.eeg_buffer.outgoing()

            if timestamp is None or new_data is None:
                continue

            yield from self.processor.process(t_init, timestamp, new_data)
