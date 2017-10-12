### DEPRECATED!!

"""Module that provides classes to handle the connections."""
from time import time
from collections import deque
import threading
import numpy as np
import pandas as pd
import basic
from backend import tf, info
from . import calibrators as crs, yielders

class DataBuffer:
    """Receives incoming data and provides a generator to yield it."""

    def __init__(self, name="", maxsize=10, yield_function=None):
        """Initialize."""
        self.name = name

        # All the data
        self._full_time = []
        self._full_data = []
        self.lock_l = threading.Lock() # Lock lists

        # Queues para stream de datos, # thread safe
        self._q_time = deque(maxlen=maxsize)
        self._q_data = deque(maxlen=maxsize)
        self.lock_q = threading.Lock() # Lock queues

        # Yielder
        self._yielder = yield_function

    def start_calibrating(self):
        """Method to start calibrating, override it."""
        # print("{} buffer can't stream calibrated data".format(self.name))
        return False

    def stop_calibrating(self):
        """Method to stop calibrating, override it."""
        # print("{} buffer can't stream calibrated data".format(self.name))
        return False

    def start_collecting(self):
        """Start collecting baseline data to detect emotions."""
        return False

    def stop_collecting(self):
        """Stop collecting data to detect emotions."""
        return False

    def incoming_data(self, timestamps, new_data):
        """Process the incoming data."""
        # Add to full lists
        with self.lock_l:
            self._full_time.append(timestamps)
            self._full_data.append(new_data)

        # Add to queue
        with self.lock_q:
            self._q_time.append(timestamps)
            self._q_data.append(new_data)

    def data_generator(self, n_data=None):
        """Generator to stream the data.

        Parameters:
        n_data -- parameter passed to the yielder"""

        if self._yielder is None:
            basic.perror("Can't stream the data without a yielder")

        yield "event: config\ndata: eeg\n\n" # Start message

        with self.lock_q:
            # Drop old data in queue
            self._q_time.clear()
            self._q_data.clear()
            t_init = time() # Set an initial time as marker

        while True:
            self.lock_q.acquire()
            if len(self._q_time) == 0 or len(self._q_data) == 0: # NOTE: both lengths should always be the same
                self.lock_q.release()
                continue

            t = self._q_time.popleft()
            d = self._q_data.popleft()
            self.lock_q.release()

            yield from self._yielder(t, t_init, d, n_data)

class WaveBuffer(EEGBuffer):
    """Buffer to stream waves data (alpha, beta, etc)."""

    def __init__(self, name="", window=256, step=25, srate=256, test_population=False, feeling_interval=1):
        """Initialize."""
        super().__init__(name, maxsize=None, yield_function=None)

        # TODO: delete queue and yielder created in super() (so they don't waste space)

        # This class needs a client to work fine
        self.is_stream_connected = False

        # Buffer # HACK: 12 samples and 6 (5chs + time) hardcoded
        self._size_buffer = 12*1000 # HACK: define adecuate value (instead of 1000)
        self._buffer = np.zeros((6, self._size_buffer))

        # Pointers to the buffer
        self._start = 0 # Inclusive # The first data is in _start (if _end is bigger)
        self._end = 0 # Exclusive # There is no data in _end

        # Lock to use anything from the buffer
        self._lock_b = threading.Lock()

        # Parameters to perform stfft
        self.window = window
        self.step = step

        # Status of the wave (about calibration)
        self.calibrator = crs.WaveDivider() # REVIEW: move calibrator to base class DataBuffer?

        # Array of frequencies
        arr_freqs = tf.get_arr_freqs(window, srate)

        # Yielder # REVIEW: here yielder is an object, in the other buffers is a function
        self._yielder = yielders.WaveYielder(np.array(arr_freqs))

        # Feel indicator
        waves_freq = int(window/step)
        self.feeler = crs.FeelCalculator(np.array(arr_freqs),
                    test_population=test_population,
                    limit_population=waves_freq*feeling_interval)

        self.levels_times = []
        self.levels_relaxation = []
        self.levels_concentration = []

    def start_calibrating(self):
        """Set the status to start recording calibrating data."""
        if not self.is_stream_connected:
            print("Can't start calibrating if it isn't streaming") # REFACTOR: error msg
            return False
        return self.calibrator.start_calibrating()

    def stop_calibrating(self):
        """Set the status to stop recording calibrating data."""
        return self.calibrator.stop_calibrating()

    def start_collecting(self):
        """Start collecting baseline data to detect emotions."""
        if self.calibrator.is_calibrated():
            return self.feeler.start_calibrating()
        else:
            print("You must calibrate the data before collecting") # REFACTOR: error msg
            return False

    def stop_collecting(self):
        """Stop collecting data to detect emotions."""
        if self.calibrator.is_calibrated():
            return self.feeler.stop_calibrating()
        else:
            print("You must calibrate the data before collecting") # REFACTOR: error msg
            return False

    def incoming_data(self, timestamps, new_data):
        """Override the method for incoming data."""
        # Add eeg to full lists
        with self.lock_l:
            self._full_time.append(timestamps)
            self._full_data.append(new_data)

        n_chs, n_data = new_data.shape

        # Add data to buffer array
        with self._lock_b:
            # Check if new data fits
            new_end = self._end + n_data
            if new_end >= self._size_buffer: # The data would overflow (out of the buffer)
                n_useful = self._end - self._start # Useful data

                if n_useful + n_data <= self._size_buffer: # All data (old + new) fits
                    # Copy the old useful data to the beginning
                    self._buffer[:, :n_useful] = self._buffer[:, self._start:self._end]

                    # move start and end
                    self._start = 0
                    self._end = n_useful
                    new_end = self._end + n_data
                else: # All the data doesn't fit
                    # Solution: erase useful data, start over # Bad solution?
                    self._start = 0
                    self._end = 0
                    new_end = self._end + n_data


            # Copy the new data to buffer
            self._buffer[0, self._end:new_end] = timestamps # Copy time
            self._buffer[1:, self._end:new_end] = new_data # Copy data
            self._end = new_end # Move end

    def data_generator(self):
        """Generator to stream the data."""

        self.is_stream_connected = True

        yield "event: config\ndata: waves\n\n"

        # Mark the time
        with self._lock_b:
            self._start = self._end
            t_init = time() # Set an initial time as marker

        # Start transmitting
        while True:
            self._lock_b.acquire()
            if self._end - self._start < self.window: # No enough data to make a window
                self._lock_b.release()
                continue

            # Copy data to a new array
            end = self._start + self.window # End of the useful data
            t = self._buffer[0, end - 1] # Get last timestamp
            d = np.copy(self._buffer[1:, self._start:end]) # Copy the rest of the channels

            # Move start
            self._start += self.step
            self._lock_b.release()

            # Normalize time
            t_normalized = t - t_init

            # Calculate TF
            power = tf.apply_fft(d) # shape: (n_chs, n_freqs)

            # Calibrate, if any
            power = self.calibrator.calibrate(power)

            # Detect emotion
            feeling = self.feeler.feel(power)

            if not feeling is None:
                # print(feeling) # DEBUG
                self.levels_times.append(t)
                self.levels_relaxation.append(feeling[0])
                self.levels_concentration.append(feeling[1])

            # Yield waves
            yield from self._yielder.yield_function(t_normalized, power)

    def get_feelings(self):
        """Return a pd.DataFrame with the feelings. Not thread safe"""
        if len(self.levels_times) == 0:
            basic.perror("get_feelings(), No feelings found")

        timestamps = np.array(self.levels_times) - self._full_time[0][0]

        feelings_df = pd.DataFrame()
        feelings_df[info.colname_timestamps] = timestamps
        feelings_df[info.colname_relaxation] = self.levels_relaxation
        feelings_df[info.colname_concentration] = self.levels_concentration

        return feelings_df
