import threading
import numpy as np
from time import sleep

def random_float(min_num, max_num):
    """Random float."""
    dx = np.random.random()
    dy_dx = (max_num - min_num)
    return min_num + dy_dx * dx

class MuseFaker:
    """Fake a muse device by streaming random data."""

    def __init__(self, **config):
        self.callback_eeg = config['callback_eeg']
        self._is_running = False

        # values hardcoded, they are from the muse configuration
        srate = 256
        self.n_samples = 12
        self.n_channels = 5

        self.waiting_time = 1 / srate

    def connect(self, **kwargs):
        self.generate_thread = threading.Thread(target=self._generate_random_data, daemon=True)

    def disconnect(self):
        pass

    def start(self):
        self._is_running = True
        self.generate_thread.start()

    def stop(self):
        self._is_running = False
        self.generate_thread.join()

    def ask_config(self):
        print("This is a Fake muse!")

    def _random_sine_waves(self, timestamps):
        """Return an array of shape (n_channels, len(timestamps)), where each channel have a randomly generated sine wave."""
        # Time
        n_points = len(timestamps)
        time_array = np.linspace(0, 1, n_points)

        all_waves = []

        # Iterate waves
        for ch_i in range(self.n_channels):
            # Empty sine wave
            sine_wave = np.zeros(n_points)

            # Amount of sines to sum up
            n_sines = np.random.randint(2, 5)

            for sine_i in range(n_sines):
                freq = random_float(4, 50)
                amp = random_float(50, 100)
                phase = random_float(0, 1)

                # Add sine wave
                sine_wave += np.sin(2*np.pi*freq*time_array + phase) * amp

            all_waves.append(sine_wave)

        return np.array(all_waves)

    def _generate_random_data(self):
        current_time = 0

        while self._is_running:
            next_time = current_time + self.waiting_time
            # NOTE: assume that generating random waves takes 0 seconds

            # Create data
            timestamps = np.linspace(current_time, next_time, self.n_samples)
            data = self._random_sine_waves(timestamps)

            self.callback_eeg(timestamps, data)

            current_time = next_time
            sleep(self.waiting_time)
