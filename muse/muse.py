import bitstring
import pygatt
import numpy as np
from time import time, sleep
from sys import platform


class Muse():
    """Muse 2016 headband"""

    def __init__(self, address, callback, eeg=True, accelero=False,
                 giro=False, backend='auto', interface=None, time_func=time):
        """Initialize"""
        self.address = address
        self.callback = callback
        self.eeg = eeg
        self.accelero = accelero
        self.giro = giro
        self.interface = interface
        self.time_func = time_func

        if backend in ['auto', 'gatt', 'bgapi']:
            if backend == 'auto':
                if platform == "linux" or platform == "linux2":
                    self.backend = 'gatt'
                else:
                    self.backend = 'bgapi'
            else:
                self.backend = backend
        else:
            raise(ValueError('Backend must be auto, gatt or bgapi'))

    def connect(self, interface=None, backend='auto'):
        """Connect to the device"""

        if self.backend == 'gatt':
            self.interface = self.interface or 'hci0'
            self.adapter = pygatt.GATTToolBackend(self.interface)
        else:
            self.adapter = pygatt.BGAPIBackend(serial_port=self.interface)

        self.adapter.start()
        try:
            self.device = self.adapter.connect(self.address)
        except Exception as e:
            return 1 #Error

        # subscribes to EEG stream
        if self.eeg:
            self._subscribe_eeg()

        # subscribes to Accelerometer
        if self.accelero:
            raise(NotImplementedError('Accelerometer not implemented'))

        # subscribes to Giroscope
        if self.giro:
            raise(NotImplementedError('Giroscope not implemented'))

        return 0 #Success

    def start(self):
        """Start streaming."""
        self._init_sample()
        self.device.char_write_handle(0x000e, [0x02, 0x64, 0x0a], False)

    def stop(self):
        """Stop streaming."""
        self.device.char_write_handle(0x000e, [0x02, 0x68, 0x0a], False)

    def disconnect(self):
        """disconnect."""
        self.device.disconnect()
        self.adapter.stop()

    def _subscribe_eeg(self):
        """subscribe to eeg stream."""
        self.device.subscribe('273e0003-4c4d-454d-96be-f03bac821358',
                              callback=self._handle_eeg)
        self.device.subscribe('273e0004-4c4d-454d-96be-f03bac821358',
                              callback=self._handle_eeg)
        self.device.subscribe('273e0005-4c4d-454d-96be-f03bac821358',
                              callback=self._handle_eeg)
        self.device.subscribe('273e0006-4c4d-454d-96be-f03bac821358',
                              callback=self._handle_eeg)
        self.device.subscribe('273e0007-4c4d-454d-96be-f03bac821358',
                              callback=self._handle_eeg)

    def _unpack_eeg_channel(self, packet):
        """Decode data packet of one eeg channel.

        Each packet is encoded with a 16bit timestamp followed by 12 time
        samples with a 12 bit resolution.
        """
        aa = bitstring.Bits(bytes=packet)
        pattern = "uint:16,uint:12,uint:12,uint:12,uint:12,uint:12,uint:12, \
                   uint:12,uint:12,uint:12,uint:12,uint:12,uint:12"
        res = aa.unpack(pattern)
        timestamp = res[0]
        data = res[1:]
        # 12 bits on a 2 mVpp range
        data = 0.48828125 * (np.array(data) - 2048)
        return timestamp, data

    def _init_sample(self):
        """initialize array to store the samples"""
        self.timestamps = np.zeros(5)
        self.data = np.zeros((5, 12))

    def _handle_eeg(self, handle, data):
        """Calback for receiving a sample.

        sample are received in this oder : 44, 41, 38, 32, 35
        wait until we get 35 and call the data
        """
        timestamp = self.time_func()
        index = int((handle - 32) / 3)
        tm, d = self._unpack_eeg_channel(data)
        self.data[index] = d
        self.timestamps[index] = timestamp
        # last data received
        if handle == 35:
            # affect as timestamps the first timestamps - 12 sample
            timestamps = np.arange(-12, 0) / 256.
            timestamps += np.min(self.timestamps)
            self.callback(self.data, timestamps)
            self._init_sample()
