import threading
import numpy as np
import pandas as pd
import basic
from backend import info

class EEGCollector:
    """Collects the eeg into one big list.

    Some methods are thread safe, i.e. to be used from: incoming data (muse data) and program handler (query last time and stuff)"""

    def __init__(self):
        self._full_time = []
        self._full_data = []
        self._lock_l = threading.Lock() # Lock lists

    def collect(self, timestamps, new_data):
        """Collect new incoming data."""
        with self._lock_l:
            self._full_time.append(timestamps)
            self._full_data.append(new_data)

    def get_running_time(self):
        """Return the time that it has been running. Thread safe"""

        with self._lock_l:
            if len(self._full_time) == 0:
                return 0

            t_end = self._full_time[-1][-1]
            t_init = self._full_time[0][0]

        elapsed_time = t_end - t_init
        return basic.sec2hr(elapsed_time)

    def get_last_timestamp(self):
        """Return the last timestamp. Thread safe"""
        with self._lock_l:
            return self._full_time[-1][-1]

    def normalize_marks(self, marks):
        """Receive a marks list (timestamps), normalize the time."""
        ## REFACTOR:
        ## change this function by:
        # def get_first_timestamp(self):
        #     pass
        return np.array(marks) - self._full_time[0][0]

    def _normalize_time(self, times=None):
        """Concatenate and return its timestamps."""
        timestamps = np.concatenate(times or self._full_time)
        return timestamps - timestamps[0]

    def _normalize_data(self):
        """Return the data concatenated"""
        return np.concatenate(self._full_data, 1).T

    def generate_eeg_df(self):
        """Return the eeg data as a pd.DataFrame.

        Not thread safe
        It doesn't affect the saved data since it creates copies"""

        if len(self._full_time) == 0 or len(self._full_data) == 0:
            return None

        timestamps = self._normalize_time()
        eeg_data = self._normalize_data()

        eeg_df = pd.DataFrame(data=eeg_data, columns=info.get_chs_muse(aux=True))
        eeg_df[info.colname_timestamps] = timestamps

        return eeg_df
