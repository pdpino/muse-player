import threading
import numpy as np

class EEGWindowBuffer():
    """Buffer to send the outgoing data in windows of a defined length."""

    def __init__(self, window=256, step=25):
        """Initialize."""

        # values hardcoded
        n_samples = 12 # samples of each muse message
        n_chs = 6 # 5chs + time

        # Buffer
        self._size_buffer = n_samples * 1000 # HACK: define adecuate value (instead of 1000)
        self._buffer = np.zeros((n_chs, self._size_buffer))

        # Pointers to the buffer
        self._start = 0 # Inclusive # The first data is in _start (if _end is bigger)
        self._end = 0 # Exclusive # There is no useful data in _end

        # Lock to use anything from the buffer
        self._lock_b = threading.Lock()

        # Parameters to move the buffer
        self.window = window
        self.step = step

    def clear(self):
        """Clear the buffer."""
        with self._lock_b:
            self._start = self._end

    def incoming(self, timestamps, new_data):
        """Store the incoming data into the buffer."""

        n_chs, n_data = new_data.shape

        # Add data to buffer array
        with self._lock_b:
            # Check if new data fits
            new_end = self._end + n_data

            if new_end >= self._size_buffer: # The data would overflow (out of the buffer)
                n_useful = self._end - self._start # Amount of useful data

                # Check if all the data (old + new) fits
                if n_useful + n_data <= self._size_buffer: # it fits
                    # Copy the old useful data to the beginning
                    self._buffer[:, :n_useful] = self._buffer[:, self._start:self._end]

                    # move start and end
                    self._start = 0
                    self._end = n_useful
                else: # does not fit
                    # Solution: erase useful data, start over
                    # REVIEW: Bad solution?
                    self._start = 0
                    self._end = 0

                # Recalculate new_end
                new_end = self._end + n_data

            # Copy the new data to buffer
            self._buffer[0, self._end:new_end] = timestamps # Copy time
            self._buffer[1:, self._end:new_end] = new_data # Copy data
            self._end = new_end # Move end

    def outgoing(self):
        """Return the next outgoing data.

        Returns timestamps, new_data
        timestamps -- float
        new_data -- np.array of shape (n_chs, window)
            n_chs here doesn't count the time (only data channels)"""

        self._lock_b.acquire()
        if self._end - self._start < self.window: # No enough data to make a window
            self._lock_b.release()
            return None, None

        # Copy data to a new array
        end = self._start + self.window # End of the useful data
        timestamp = self._buffer[0, end - 1] # Get last timestamp
        new_data = np.copy(self._buffer[1:, self._start:end]) # Copy the rest of the channels

        # Move start
        self._start += self.step
        self._lock_b.release()

        return timestamp, new_data
