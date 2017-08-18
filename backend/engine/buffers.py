"""Module that provides classes to handle the connections."""
from time import time
from collections import deque
import threading
import numpy as np
import pandas as pd
from enum import Enum
import basic
from backend import data, tf, info

class WaveCalibStatus(Enum):
    """Status of the calibration of the wave."""
    No = 0 # There is no calibration
    Start = 1 # A start_calibrating() signal has been received
    Calibrating = 2 # Currently saving baseline
    Stop = 3 # A stop_calibrating() signal has been received
    Yes = 4 # The baseline is already saved and the data is being normalized


class DataBuffer(object):
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
        print("{} buffer can't stream calibrated data".format(self.name))

    def stop_calibrating(self):
        """Method to stop calibrating, override it."""
        print("{} buffer can't stream calibrated data".format(self.name))


    def incoming_data(self, timestamps, data):
        """Process the incoming data."""
        # Add to full lists
        with self.lock_l:
            self._full_time.append(timestamps)
            self._full_data.append(data)

        # Add to queue
        with self.lock_q:
            self._q_time.append(timestamps)
            self._q_data.append(data)

    def data_generator(self, n_data=None):
        """Generator to stream the data.

        Parameters:
        n_data -- parameter passed to the yielder"""

        if self._yielder is None:
            basic.perror("Can't stream the data without a yielder")
            return # NOTREACHED

        with self.lock_q:
            # Drop old data in queue
            self._q_time.clear()
            self._q_data.clear()
            t_init = time() # Set an initial time as marker

        # yield "event: start\ndata: 0\n\n" # Start message
        yield "data: 0\n\n" # Start message # REVIEW: send other type of message?

        while True:
            self.lock_q.acquire()
            if len(self._q_time) == 0 or len(self._q_data) == 0: # NOTE: both lengths should always be the same
                self.lock_q.release()
                continue

            t = self._q_time.popleft()
            d = self._q_data.popleft()
            self.lock_q.release()

            yield from self._yielder(t, t_init, d, n_data)

class EEGBuffer(DataBuffer):
    """Contains the eeg data produced by Muse, provides provides functionality for eeg data"""
    def get_running_time(self):
        """Return the time that it has been running.

        It is not thread safe, use it only when the incoming data has stopped"""
        if len(self._full_time) == 0:
            return 0

        t_end = self._full_time[-1][-1]
        t_init = self._full_time[0][0]
        t = t_end - t_init
        return basic.sec2hr(t)

    def get_last_timestamp(self):
        """Return the last timestamp. Thread safe"""
        with self.lock_l:
            return self._full_time[-1][-1]

    def normalize_marks(self, marks):
        """Receive a marks list (timestamps), normalize the time."""
        return np.array(marks) - self._full_time[0][0]

    def _normalize_time(self):
        """Concatenate and return its timestamps."""

        # Concat y normalizar timestamps
        timestamps = np.concatenate(self._full_time)
        return timestamps - timestamps[0]

    def _normalize_data(self):
        """Return the data concatenated"""
        return np.concatenate(self._full_data, 1).T

    def save_csv(self, fname, subfolder=None, suffix=None):
        """Preprocess the data and save it to a csv.

        It doesn't affect the saved data, creates copies"""
        if len(self._full_time) == 0 or len(self._full_data) == 0:
            return

        # Concatenar data
        timestamps = self._normalize_time()
        eeg_data = self._normalize_data()

        # Juntar en dataframe
        res = pd.DataFrame(data=eeg_data, columns=info.get_chs_muse(aux=True))
        res[info.timestamps_column] = timestamps

        # Guardar a csv
        data.save_eeg(res, fname, subfolder, suffix)

class WaveBuffer(EEGBuffer):
    """Buffer to stream waves data (alpha, beta, etc)."""

    def __init__(self, name="", window=256, step=25, srate=256):
        """Initialize."""
        super().__init__(name, maxsize=None, yield_function=None)

        # TODO: delete queue and yielder (so they don't waste space)


        # Buffer # HACK: 12 samples and 6 (5chs + time) hardcoded
        self._size_buffer = 12*1000 # TODO: define adecuate value
        self._buffer = np.zeros((6, self._size_buffer))

        # Pointers to the buffer
        self._start = 0 # Inclusive # The first data is in _start (if _end is bigger)
        self._end = 0 # Exclusive # There is no data in _end

        # Lock to use anything from the buffer
        self._lock_b = threading.Lock()

        # Parameters to perform stfft
        self.window = window
        self.step = step

        # Array of frequencies to order the fft
        self.arr_freqs = tf.get_arr_freqs(window, srate)

        # Status of the wave (about calibration)
        self._lock_s = threading.Lock() # Lock the status
        self.status = WaveCalibStatus.No
        self._is_calibrated = False
        # self.calib_callback = calib_callback # DEBUG: to use a notify callback

    def start_calibrating(self):
        """Set the status to start recording calibrating data."""
        with self._lock_s:
            self.status = WaveCalibStatus.Start

    def stop_calibrating(self):
        """Set the status to stop recording calibrating data."""
        with self._lock_s:
            if self.status == WaveCalibStatus.Calibrating:
                self.status = WaveCalibStatus.Stop

    def incoming_data(self, timestamps, data):
        """Override the method for incoming data."""
        # Add eeg to full lists
        with self.lock_l:
            self._full_time.append(timestamps)
            self._full_data.append(data)

        n_chs, n_data = data.shape

        # Add data to buffer array
        with self._lock_b:
            # Check if new data fits
            new_end = self._end + n_data
            if new_end >= self._size_buffer: # The data would overflow (out of the buffer)
                n_useful = self._end - self._start # Useful data

                if n_useful + n_data <= self._size_buffer: # All data (old + new) fits
                    # print("moving to the beginning") # DEBUG
                    # Copy the old useful data to the beginning
                    self._buffer[:, :n_useful] = self._buffer[:, self._start:self._end]

                    # move start and end
                    self._start = 0
                    self._end = n_useful
                    new_end = self._end + n_data
                else: # All the data doesn't fit
                    # print("erasing") # DEBUG
                    # Solution: erase useful data, start over # Bad solution?
                    self._start = 0
                    self._end = 0
                    new_end = self._end + n_data


            # Copy the new data to buffer
            self._buffer[0, self._end:new_end] = timestamps # Copy time
            self._buffer[1:, self._end:new_end] = data # Copy data
            self._end = new_end # Move end

    def data_generator(self):
        """Generator to stream the data."""

        # Drop old data in buffer
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
            t = self._buffer[0, self._end - 1] # Get last timestamp
            d = np.copy(self._buffer[1:, self._start:self._start + self.window]) # Copy the rest of the channels

            # Move start
            self._start += self.step
            self._lock_b.release()

            # Normalize time
            t -= t_init

            # Calculate TF
            power = tf.apply_fft(d) # shape: (n_chs, n_freqs)

            # Check status of calibration
            with self._lock_s: # Get status
                status = self.status

            if status == WaveCalibStatus.Start:
                # Signal has been received, start variables
                calib_arr = np.zeros(power.shape)
                calib_counter = 0

                # Change status to start calibrating in the next iteration
                with self._lock_s:
                    self.status = WaveCalibStatus.Calibrating

            elif status == WaveCalibStatus.Calibrating:
                # Add data to the array
                calib_arr += power
                calib_counter += 1

            elif status == WaveCalibStatus.Stop:
                # Average the collected data
                if calib_counter > 0:
                    calib_arr /= calib_counter
                    self._is_calibrated = True
                    with self._lock_s: # Set status to yes
                        self.status = WaveCalibStatus.Yes


            elif status == WaveCalibStatus.Yes:
                # Use baseline data to normalize
                # power = tf.normalize_power(power, calib_arr)
                power = 10*np.log10(power/calib_arr)


            # NOTE: if status is No, just send non-calibrated waves to client


            # Get waves
            deltas = tf.get_wave(power, self.arr_freqs, 1, 4)
            thetas = tf.get_wave(power, self.arr_freqs, 4, 8)
            alphas = tf.get_wave(power, self.arr_freqs, 8, 13)
            betas = tf.get_wave(power, self.arr_freqs, 13, 30)
            gammas = tf.get_wave(power, self.arr_freqs, 30, 44)

            channel = 0 # DEBUG

            # Yield
            yield "data: {}, {}, {}, {}, {}, {}\n\n".format(t,
                deltas[channel],
                thetas[channel],
                alphas[channel],
                betas[channel],
                gammas[channel])

            # HACK: use yielders? There could be an option of what to yield (alphas from all, waves from one channel or everything)
