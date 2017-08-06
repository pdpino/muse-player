"""Module that provides classes to handle the connections."""
from time import time
from collections import deque
import threading
import numpy as np
import pandas as pd
import basic
from backend import data

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
            return

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
        res = pd.DataFrame(data=eeg_data, columns=['TP9', 'AF7', 'AF8', 'TP10', 'Right AUX'])
        res['timestamps'] = timestamps

        # Guardar a csv
        data.save_eeg(res, fname, subfolder, suffix)

class DataYielder(object):
    """Yield functions to stream any data in the desired way."""

    yield_string = "data: {}, {}\n\n"

    @staticmethod
    def get_data(t, t_init, data, dummy=None):
        """Yield out all the points in the data."""
        data_str = ','.join(map(str, data))
        a = DataYielder.yield_string.format(t - t_init, data_str)
        yield a

class EEGYielder(object):
    """Yield functions to stream the eeg data in the desired way.

    Assumes that the shape of the data is:
    len(t) == 12
    d.shape == (5, 12)"""

    # String para hacer yield
    # EEG envia (timestamp, ch0, ch1, ch2, ch3, ch4)
    yield_string = "data: {}, {}, {}, {}, {}, {}\n\n"

    @staticmethod
    def _get_data_mean(t, t_init, data, dummy=None):
        """Yield the mean in the 12 samples for each channel separately."""
        yield EEGYielder.yield_string.format( \
                t.mean() - t_init, \
                data[0].mean(), \
                data[1].mean(), \
                data[2].mean(), \
                data[3].mean(), \
                data[4].mean() )

    @staticmethod
    def _get_data_max(t, t_init, data, dummy=None):
        """Yield the max of the 12 samples for each channel separately"""
        # NOTE: use tt.max(), tt.mean()?
        yield EEGYielder.yield_string.format( \
                t.max() - t_init, \
                data[0].max(), \
                data[1].max(), \
                data[2].max(), \
                data[3].max(), \
                data[4].max() )

    @staticmethod
    def _get_data_min(t, t_init, data, dummy=None):
        """Yield the min of the 12 samples for each channel separately"""
        yield EEGYielder.yield_string.format( \
                t.min() - t_init, \
                data[0].min(), \
                data[1].min(), \
                data[2].min(), \
                data[3].min(), \
                data[4].min() )

    @staticmethod
    def _get_data_n(t, t_init, data, n):
        """Yield n out of the 12 samples."""
        for i in range(n):
            tt = t[i] - t_init
            yield EEGYielder.yield_string.format(
                tt, \
                data[0][i], \
                data[1][i], \
                data[2][i], \
                data[3][i], \
                data[4][i] )

    @staticmethod
    def get_yielder(mode):
        """Return the selected yielder function"""
        # Available yielders
        yielders = {
            "mean": EEGYielder._get_data_mean,
            "min": EEGYielder._get_data_min,
            "max": EEGYielder._get_data_max,
            "n": EEGYielder._get_data_n
            }

        try:
            yielder = yielders[mode]
        except KeyError:
            basic.perror("yielder: {} not found".format(mode), force_continue=True)
            yielder = EEGYielder._get_data_n # Default

        return yielder
