"""MusePlayer class."""
from time import sleep
import threading
from flask import Response, Flask   # Stream data to client
from flask_cors import CORS
from backend import filesystem, engine, info, tf, basic
from backend.muse import Muse, MuseFaker
from .commands import CommandHandler

class MusePlayer:
    """Handles muse sending data, engine to process that data, and a Flask streamer"""

    def __init__(self):
        # Connection
        self.is_playing = False

        # Marks in time
        self.mark_timestamps = []
        self.mark_messages = []

    def initialize_command_handler(self):
        """Set basic commands into command handler."""

        self.commands = CommandHandler()

        def ask_muse_config():
            """Send a signal to the muse to get configuration status."""
            self.muse.ask_config()
            sleep(0.5) # let it print # REVIEW: wait for printing explicitly?

        self.commands.add_command("-c", ask_muse_config, None, None, cmd_help="Get muse configuration status")

    def _get_regulator(self, regulator_type, accum_samples=10):

        # TODO: make this a set_regulator method

        if regulator_type == "accum":
            regulator = engine.collectors.DataAccumulator(samples=accum_samples)
        elif regulator_type == "calib":
            regulator = engine.calibrators.Calibrator(engine.calibrators.BaselineFeeling())
            self.commands.add_command("-3", regulator.signal_start_calibrating, info.start_collect_mark, 'notification')
            self.commands.add_command("-4", regulator.signal_stop_calibrating, info.stop_collect_mark, 'notification')
        else:
            regulator = None

        return regulator

    def initialize_eeg_engine(self, stream_type, regulator_type, eeg_mode=None, eeg_n=None, waves_selected=None, accum_samples=None):
        """Initialize the EEG engine."""
        self.stream_enabled = not stream_type is None

        stream_type = stream_type or "eeg" # DEFAULT

        # Select processor for the EEG data # REFACTOR: use dicts to hold configurations ??
        if stream_type == "eeg":
            self.eeg_buffer = engine.buffers.EEGBuffer()

            generator = engine.EEGRawYielder(eeg_mode, stream_n=eeg_n)

        elif stream_type == "waves":
            self.eeg_buffer = engine.buffers.EEGWindowBuffer()

            # Create wave yielder
            window = 256 # HACK: values for the yielder hardcoded
            srate = 256
            channel = 0
            arr_freqs = tf.get_freqs_resolution(window, srate)
            wave_yielder = engine.yielders.WaveYielder(arr_freqs, channel=channel, waves=waves_selected)

            generator = engine.WaveProcessor(wave_yielder)

        elif stream_type == "feel":
            self.eeg_buffer = engine.buffers.EEGWindowBuffer()

            feeler = engine.feelers.FeelerRelaxConc()
            regulator = self._get_regulator(regulator_type, accum_samples)
            self.feel_processor = engine.FeelProcessor(feeler, regulator)
            generator = engine.WaveProcessor(self.feel_processor)

        elif stream_type == "feel_val_aro":
            self.eeg_buffer = engine.buffers.EEGWindowBuffer()

            feeler = engine.feelers.FeelerValAro()
            regulator = self._get_regulator(regulator_type, accum_samples)
            self.feel_processor = engine.FeelProcessor(feeler, regulator)
            generator = engine.WaveProcessor(self.feel_processor)

        else:
            basic.perror("Stream type not recognized: {}".format(stream_type))

        # Engine that handles the incoming, processing and outgoing data
        self.eeg_collector = engine.collectors.EEGCollector()
        self.eeg_engine = engine.EEGEngine(stream_type, self.eeg_collector, self.eeg_buffer, generator)

    def initialize_acc_engine(self):
        """Initialize the engine."""

        # HACK: the EEG buffer should do it (for now)
        # don't use peek_last_time although!!
        acc_buffer = engine.buffers.EEGBuffer()

        acc_yielder = engine.yielders.AccYielder()
        generator = engine.processors.AccProcessor(acc_yielder)

        self.acc_engine = engine.ImuEngine("Accelerometer", acc_buffer, generator)

    def initialize_muse(self, muse_address, interface, faker=False, nfactor=None, nsub=None):
        """Initialize muse connection."""

        def print_control_message(codes, message):
            print("\t", message)

        def print_telemetry(timestamp, battery, temperature):
            print("\tbattery: {}%, temperature: {}".format(battery, temperature))

        if faker:
            self.muse = MuseFaker(callback_eeg=self.eeg_engine.incoming_data)
        else:
            self.muse = Muse(address=muse_address,
                        callback_eeg=self.eeg_engine.incoming_data,
                        # callback_control=print_control_message,
                        # callback_telemetry=print_telemetry,
                        callback_acc=self.acc_engine.incoming_data,
                        norm_factor=nfactor, norm_sub=nsub)
        self.muse.connect(interface=interface)

    def initialize_flask(self, ip, port, url):
        """Initialize flask connection."""
        if not self.stream_enabled:
            return

        print("Streaming enabled")

        app = Flask(__name__)
        CORS(app) # Cross-origin resource sharing (so web app can access other ports)

        # Stream thread
        self.stream = threading.Thread(target=app.run, kwargs={"host": ip, "port": port, "threaded": True})
        self.stream.daemon = True

        # Connect data to send
        @app.route(url)
        def stream_data():
            """Stream the eeg data."""
            return Response(self.eeg_engine.outgoing_data(), mimetype="text/event-stream")

        @app.route("/acc")
        def stream_accelerometer():
            return Response(self.acc_engine.outgoing_data(), mimetype="text/event-stream")

    def _stream_forever(self):
        """Stream until interrupted """
        # Wait for a buffer zone
        sleep(1)

        try:
            while True:
                message = input("cmd: ")
                timestamp = self.eeg_collector.get_last_timestamp()

                # Special commands
                if self.commands.exist_command(message):
                    message = self.commands.apply_command(message)
                    if message is None:
                        continue

                # Save
                self.mark_timestamps.append(timestamp)
                self.mark_messages.append(message.lower())
        except KeyboardInterrupt:
            print("Exiting")
            basic.mute_ctrlc() # So the finishing process isn't interrupted

    def _stream_for(self, time):
        """Stream for a determined amount of time.

        TODO: habilitate commands and marks with this option"""
        basic.mute_ctrlc()
        print("\tfor (aprox) {} seconds".format(time))
        sleep(time) # HACK: its aprox time

    def start(self, for_time=None):
        self.muse.start()
        if self.stream_enabled:
            self.stream.start()

        self.is_playing = True
        print("Started receiving data")

        if for_time is None:
            self._stream_forever()
        else:
            self._stream_for(for_time)

        self.muse.stop()
        self.muse.disconnect() # FIXME: sometimes a thread gets stuck here

        self.is_playing = True

        print("Stopped receiving data, received for {}".format(self.eeg_collector.get_running_time()))

    def save(self, fname, subfolder):
        """Save data collected."""
        if self.is_playing:
            print("Can't save data if still streaming")
            return

        # Save eeg data
        eeg = self.eeg_collector.export()
        filesystem.save_eeg(fname, eeg, folder=subfolder)

        # Save marks
        self.mark_timestamps = self.eeg_collector.normalize_marks(self.mark_timestamps)
        filesystem.save_marks(fname, self.mark_timestamps, self.mark_messages, folder=subfolder)

        # Save feelings, if any
        try: # HACK: use something more elegant than try catch
            feelings = self.feel_processor.export()
            if not feelings is None:
                filesystem.save_feelings(fname, feelings, folder=subfolder)
        except UnboundLocalError as e:
            pass


# DEPRECATED
# FIXME: missing signals
# def _set_generator_commands(self):
#     self.commands.add_command("-1", generator.signal_start_calibrating, info.start_calib_mark, "notification")
#     self.commands.add_command("-2", generator.signal_stop_calibrating, info.stop_calib_mark, "notification")
