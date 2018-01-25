from time import time, sleep
from sys import platform
import struct
import numpy as np
import bitstring
import pygatt
import threading

class Muse():
    """Muse 2016 headband"""

    def __init__(self, address=None, callback_eeg=None, callback_control=None, callback_telemetry=None, callback_acc=None, callback_gyro=None, norm_factor=None, norm_sub=None):
        """Initialize

        Parameters:
        address -- MAC address for device

        callback_eeg -- function(timestamp, data) that handles incoming eeg data

        callback_control -- function(messages) that handles incoming control data

        callback_telemetry -- function(timestamp, battery, temperature) that handles incoming telemetry data

        callback_acc -- function(timestamp, samples) that handles incoming accelerometer samples
        callback_gyro -- function(timestamp, samples) that handles incoming gyroscope samples
        The imu (acc and gyro) 'samples' is a list of 3 samples, each is a dict with keys "x", "y" and "z"

        norm_factor -- Normalize factor. The eeg data is multiplied by this value, after substracting norm_sub
        norm_sub -- Normalize substractor. The eeg data gets this value substracted
        """

        # TODO: deprecate bools, use only callbacks


        self.address = address
        self.callback_eeg = callback_eeg
        self.callback_control = callback_control
        self.callback_telemetry = callback_telemetry
        self.callback_acc = callback_acc
        self.callback_gyro = callback_gyro
        self.enable_eeg = not callback_eeg is None
        self.enable_control = not callback_control is None
        self.enable_telemetry = not callback_telemetry is None
        self.enable_acc = not callback_acc is None
        self.enable_gyro = not callback_gyro is None

        self.norm_factor = 0.48828125 if norm_factor is None else norm_factor # default values used by barachant
        self.norm_sub = 2048 if norm_sub is None else norm_sub # default values used by barachant

        if self.enable_control:
            # Lock to use the messages variables, you may want to print the last message while still receiving messages!
            # REVIEW: is the lock necesary??
            self._lock_control = threading.Lock()
            self._init_control()


    """Connection methods"""

    def connect(self, preset=None, interface=None, backend='auto'):
        """Connect to the device"""

        # Define backend
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

        # Define interface
        self.interface = interface or 'hci0'

        # Connect
        if self.backend == 'gatt':
            self.adapter = pygatt.GATTToolBackend(self.interface)
        else:
            self.adapter = pygatt.BGAPIBackend(serial_port=self.interface)

        self.adapter.start()

        if self.address is None: # Scan for address
            address = self.find_muse_address()
            if address is None:
                raise(ValueError("Can't find Muse Device"))
            else:
                self.address = address

        self.device = self.adapter.connect(self.address)


        if self.enable_eeg:
            self._subscribe_eeg()

        if self.enable_control:
            self._subscribe_control()

        if self.enable_telemetry:
            self._subscribe_telemetry()

        if self.enable_acc:
            self._subscribe_acc()

        if self.enable_gyro:
            self._subscribe_gyro()

        if not preset is None:
            self._set_preset(preset)

    def _write_cmd(self, cmd):
        """Wrapper to write a command to the Muse device.

        cmd -- list of bytes"""
        self.device.char_write_handle(0x000e, cmd, False)

    def _set_preset(self, preset):
        """Send a set-preset message to Muse."""
        if preset < 20 or preset > 22:
            print("Invalid preset: {}, must be between 20 and 23".format(preset))
            return

        # TODO: Depending on the preset set, the incoming data may vary
        # not getting Right AUX, accelerometer, etc. Handle that

        num1 = 0x30 + int(preset/10)
        num2 = 0x30 + (preset % 10)

        self._write_cmd([0x04, 0x70, num1, num2, 0x0a])
        # meaning: 'pNum', where Num is preset
            # 0x04: code
            # 0x70: 'p'
            # num1, num2: preset in ASCII
            # 0x0a: '\n'

    def ask_control(self):
        """Send a message to Muse to ask for the configuration.

        Only useful if control is enabled (to receive the answer!)"""
        self._write_cmd([0x02, 0x73, 0x0a])

    def start(self):
        """Start streaming."""
        self._init_sample()
        self._write_cmd([0x02, 0x64, 0x0a])

    def stop(self):
        """Stop streaming."""
        self._write_cmd([0x02, 0x68, 0x0a])

    def disconnect(self):
        """Disconnect from device."""
        self.device.disconnect()
        self.adapter.stop()

    def find_muse_address(self):
        """Look for ble device with a muse in the name."""
        devices = []
        list_devices = self.adapter.scan(timeout=10.5)
        for device in list_devices:
            if 'Muse' in device['name']:
                return device['address']
        return None

    """Handle EEG methods"""

    def _init_sample(self):
        """initialize array to store the samples"""
        self.timestamps = np.zeros(5)
        self.data = np.zeros((5, 12))

    def _subscribe_eeg(self):
        """subscribe to eeg stream."""
        # Electrode channels
        self.device.subscribe('273e0003-4c4d-454d-96be-f03bac821358', callback=self._handle_eeg) # handle 0x20
        self.device.subscribe('273e0004-4c4d-454d-96be-f03bac821358', callback=self._handle_eeg) # handle 0x23
        self.device.subscribe('273e0005-4c4d-454d-96be-f03bac821358', callback=self._handle_eeg) # handle 0x26
        self.device.subscribe('273e0006-4c4d-454d-96be-f03bac821358', callback=self._handle_eeg) # handle 0x29
        self.device.subscribe('273e0007-4c4d-454d-96be-f03bac821358', callback=self._handle_eeg) # handle 0x2c

    def _unpack_eeg_channel(self, packet):
        """Decode data packet of one eeg channel.

        Each packet is encoded with a 16bit timestamp followed by 12 time
        samples with a 12 bit resolution.
        """
        bit_decoder = bitstring.Bits(bytes=packet)
        pattern = "uint:16,uint:12,uint:12,uint:12,uint:12,uint:12,uint:12, \
                   uint:12,uint:12,uint:12,uint:12,uint:12,uint:12"
        # pattern = "uint:16,int:12,int:12,int:12,int:12,int:12,int:12, \
        #            int:12,int:12,int:12,int:12,int:12,int:12"
        res = bit_decoder.unpack(pattern)
        timestamp = res[0]
        data = res[1:]

        # 12 bits on a 2 mVpp range
        # data = 0.48828125 * (np.array(data) - 2048) # in microVolts # default values chosen by barachant
        # NOTE: the norm factor comes from passing the unsigned ints in (0, 4096) to a float in (0, 2mV).
            # the substractor factor comes from substracting 1024 (=2048*0.488), which is done to center the data (because the hardware is AC coupled)
        data = self.norm_factor * (np.array(data) - self.norm_sub)
        return timestamp, data

    def _handle_eeg(self, handle, data):
        """Calback for receiving a sample.

        sample are received in this order : 44, 41, 38, 32, 35
        wait until we get 35 and call the data
        """
        timestamp = time()
        index = int((handle - 32) / 3)
        tm, d = self._unpack_eeg_channel(data) # timestamp from muse is ignored
        self.data[index] = d
        self.timestamps[index] = timestamp

        if handle == 35: # last data received
            # affect as timestamps the first timestamps - 12 sample
            timestamps = np.arange(-12, 0) / 256.
            timestamps += np.min(self.timestamps)
            self.callback_eeg(timestamps, self.data)
            self._init_sample()


    """Handle control messages"""

    def _init_control(self):
        with self._lock_control:
            self._current_msg = ""

    def _subscribe_control(self):
        self.device.subscribe('273e0001-4c4d-454d-96be-f03bac821358', callback=self._handle_control)

    def _handle_control(self, handle, data):
        """Handle the incoming messages from the 0x000e handle.

        Each message is 20 bytes
        The first byte, call it n, is the length of the incoming string.
        The rest of the bytes are in ASCII, and only n chars are useful

        Multiple messages together are a json object (or dictionary in python)
        If a message has a '}' then the whole dict is finished.

        Example:
        {'key': 'value',
        'key2': 'really-long
        -value',
        'key3': 'value3'}

        each line is a message, the 4 messages are a json object.
        """
        if handle != 14:
            return

        # Decode data
        bit_decoder = bitstring.Bits(bytes=data)
        pattern = "uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8, \
                    uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8"
        chars = bit_decoder.unpack(pattern)

        n_incoming = chars[0]

        incoming_message = "".join(map(chr, chars[1:]))[:n_incoming]

        with self._lock_control:
            self._current_msg += incoming_message

        if incoming_message[-1] == '}': # Message ended completely
            with self._lock_control:
                self.callback_control(self._current_msg)

            self._init_control()


    """Handle telemetry"""
    def _subscribe_telemetry(self):
        self.device.subscribe('273e000b-4c4d-454d-96be-f03bac821358', callback=self._handle_telemetry)

    def _handle_telemetry(self, handle, packet):
        """Handle the telemetry incoming data"""

        if handle != 26: # handle 0x1a
            return

        bit_decoder = bitstring.Bits(bytes=packet)
        pattern = "uint:16,uint:16,uint:16,uint:16,uint:16" # The rest is 0 padding
        data = bit_decoder.unpack(pattern)

        timestamp = data[0]
        battery = data[1] / 512
        fuel_gauge = data[2] * 2.2
        adc_volt = data[3]
        temperature = data[4]

        self.callback_telemetry(timestamp, battery, temperature)


    """Handle accelerometer and gyroscope"""
    def _unpack_imu_channel(self, packet, scale=1):
        """Decode data packet of the accelerometer and gyro channels.

        Each packet is encoded with a 16bit timestamp followed by 9 time
        samples with a 16 bit resolution.
        """
        bit_decoder = bitstring.Bits(bytes=packet)
        pattern = "uint:16,int:16,int:16,int:16,int:16, \
                   int:16,int:16,int:16,int:16,int:16"
        data = bit_decoder.unpack(pattern)

        timestamp = data[0]

        # Dict-like:
        # samples = [{
        #     "x": scale * data[index],
        #     "y": scale * data[index + 1],
        #     "z": scale * data[index + 2]
        # } for index in [1, 4, 7]]

        # List-like
        samples = [[
            scale * data[index],        # x
            scale * data[index + 1],    # y
            scale * data[index + 2]     # z
        ] for index in [1, 4, 7]]

        return timestamp, samples

    def _subscribe_acc(self):
        self.device.subscribe('273e000a-4c4d-454d-96be-f03bac821358', callback=self._handle_acc)

    def _handle_acc(self, handle, packet):
        """Handle incoming accelerometer data.

        ~17 x second"""
        if handle != 23: # handle 0x17
            return

        timestamp, samples = self._unpack_imu_channel(packet, scale=0.0000610352)

        self.callback_acc(timestamp, samples)

    def _subscribe_gyro(self):
        self.device.subscribe('273e0009-4c4d-454d-96be-f03bac821358', callback=self._handle_gyro)

    def _handle_gyro(self, handle, packet):
        """Handle incoming gyroscope data.

        ~17 x second"""
        if handle != 20: # handle 0x14
            return

        timestamp, samples = self._unpack_imu_channel(packet, scale=0.0074768)

        self.callback_gyro(timestamp, samples)

#### REVIEW:
# handle 0x1d # no recibe data
# self.device.subscribe('273e0002-4c4d-454d-96be-f03bac821358', callback=self.handle_something)

# handle 0x11 # recibe 4-5 veces por segundo
# self.device.subscribe('273e0008-4c4d-454d-96be-f03bac821358', callback=self._handle_11)
