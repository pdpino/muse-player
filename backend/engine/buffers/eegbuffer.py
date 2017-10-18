from collections import deque
import threading


class EEGBuffer:
    """Provide a simple eeg buffer.

    Buffer the incoming data (timestamps and new_data) and send it as it comes"""
    def __init__(self, maxsize=10):
        self._q_time = deque(maxlen=maxsize)
        self._q_data = deque(maxlen=maxsize)
        self._lock_q = threading.Lock() # Lock queues

    def clear(self):
        """Clear the buffer."""
        with self._lock_q:
            self._q_time.clear()
            self._q_data.clear()

    def peek_last_time(self):
        """Return the last timestamp received."""
        with self._lock_q:
            last_t = self._q_time[-1][-1]
        return last_t

    def incoming(self, timestamp, new_data):
        """Store the incoming data into the buffer."""
        with self._lock_q:
            self._q_time.append(timestamp)
            self._q_data.append(new_data)

    def outgoing(self):
        """Return the next outgoing data.

        Returns timestamp, new_data
        timestamp -- whatever came in the incoming timestamp
        new_data -- whatever came in the incoming new_data"""
        with self._lock_q:
            if len(self._q_time) > 0 and len(self._q_data) > 0:
                # NOTE: both lengths should always be the same
                timestamp = self._q_time.popleft()
                new_data = self._q_data.popleft()
            else:
                timestamp = None
                new_data = None

        return timestamp, new_data
