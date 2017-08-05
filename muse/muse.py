from time import time, sleep
from sys import platform
import struct
import numpy as np
import bitstring
import pygatt
import threading


class Muse():
    """Muse 2016 headband"""

    def __init__(self, address=None, callback=None, callback_other=None, push_info=True, eeg=True, other=True, accelero=False,
                 giro=False, norm_factor=None, norm_sub=None):
        """Initialize

        Parameters:
        address --
        callback --
        push_info -- bool, subscribe to info messages from muse and push them in screen
        eeg -- bool, subscribe to eeg streaming
        accelero -- bool, subscribe to accelerometer messages
        giro -- bool, subscribe to giroscope messages
        norm_factor -- Normalize factor. The eeg data is multiplied by this value, after substracting norm_sub
        norm_sub -- Normalize substractor. The eeg data gets this value substracted
        """


        self.address = address
        self.callback = callback
        self.callback_other = callback_other
        self.push_info = push_info
        self.other = other
        self.eeg = eeg
        self.accelero = accelero
        self.giro = giro
        self.norm_factor = 0.48828125 if norm_factor is None else norm_factor # default values used by barachant
        self.norm_sub = 2048 if norm_sub is None else norm_sub # default values used by barachant

        if push_info:
            # Lock to use the messages variables, you may want to print the last message while still receiving messages!
            self._lock_msg = threading.Lock()
            self._init_msg() # Current messages variables



        # DEBUG: reverse engineering bluetooth conn
        self.lista = []





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


        # Subscribe to messages
        if self.push_info:
            self._subscribe_admin()

        # Subscribe to other # DEBUG
        if self.other:
            # self._subscribe_other()
            pass

        # subscribes to EEG stream
        if self.eeg:
            self._subscribe_eeg()

        # subscribes to Accelerometer
        if self.accelero:
            raise(NotImplementedError('Accelerometer not implemented'))

        # subscribes to Giroscope
        if self.giro:
            raise(NotImplementedError('Giroscope not implemented'))

        if not preset is None:
            self._set_preset(preset)

    def _write_cmd(self, cmd):
        """Wrapper to write a command to the Muse device.

        cmd -- list of bytes"""
        self.device.char_write_handle(0x000e, cmd, False)

    def _set_preset(self, preset, verbose=False):
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

    def ask_config(self):
        """Ask for the config info message to Muse."""
        self._write_cmd([0x02, 0x73, 0x0a])

    """Handle EEG methods"""

    def _subscribe_eeg(self):
        """subscribe to eeg stream."""
        #### Electrode channels (tested):
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
        aa = bitstring.Bits(bytes=packet)
        pattern = "uint:16,uint:12,uint:12,uint:12,uint:12,uint:12,uint:12, \
                   uint:12,uint:12,uint:12,uint:12,uint:12,uint:12"
        # pattern = "uint:16,int:12,int:12,int:12,int:12,int:12,int:12, \
        #            int:12,int:12,int:12,int:12,int:12,int:12"
        res = aa.unpack(pattern)
        timestamp = res[0]
        data = res[1:]

        # 12 bits on a 2 mVpp range
        # data = 0.48828125 * (np.array(data) - 2048) # in microVolts # default values chosen by barachant
        # NOTE: the norm factor comes from passing the unsigned ints in (0, 4096) to a float in (0, 2mV).
            # the substractor factor comes from substracting 1024 (=2048*0.488), which is done to center the data (because the hardware is AC coupled)
        data = self.norm_factor * (np.array(data) - self.norm_sub)
        return timestamp, data

    def _init_sample(self):
        """initialize array to store the samples"""
        self.timestamps = np.zeros(5)
        self.data = np.zeros((5, 12))

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
            self.callback(timestamps, self.data)
            self._init_sample()


    """Handle Admin messages methods"""

    def _subscribe_admin(self):
        """Subscribe to administrative channels."""
        self.device.subscribe('273e0001-4c4d-454d-96be-f03bac821358', callback=self._handle_messages)

    def _init_msg(self):
        """Reset the current msg storage"""
        with self._lock_msg:
            self._current_msg = ""
            self._current_codes = []

    def _push_msg(self, codes, msg):
        """Pushes the message."""
        # Full print:
        # print("\tcodes: {}".format(codes))
        # print("\tmsg: {}".format(msg))

        # Simple print:
        print(msg)

    def _handle_messages(self, handle, data):
        """Handle the incoming messages from the 0x000e handle."""
        if handle != 14: # Messages have to be from that handle
            return

        # Decode data
        aa = bitstring.Bits(bytes=data)
        pattern = "uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8, \
                    uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8" # All are chars
        res = aa.unpack(pattern)

        # Save initial number
        with self._lock_msg:
            self._current_codes.append(res[0])

        # Iterate over next numbers
        for a in res[1:]:
            c = chr(a)

            with self._lock_msg:
                self._current_msg += c

            if c == ',': # This incoming message ended, but not the whole dict
                break

            if c == '}': # Msg ended completely
                with self._lock_msg:
                    self._push_msg(self._current_codes, self._current_msg)

                self._init_msg()
                break


    """Handle other"""
    def _subscribe_other(self):
        # DEBUG:

        ### Recibe data cada 10 segundos
        ### Handle: 0x1a = 26 # Le llegan 160 bits, sera la bateria?
        # self.device.subscribe('273e000b-4c4d-454d-96be-f03bac821358', callback=self._handle_battery)

        ### No recibe data:
        # handle 0x1d
        # self.device.subscribe('273e0002-4c4d-454d-96be-f03bac821358', callback=self.handle_something)


        ### Recibe 4-5 veces por segundo # handle 0x11
        # self.device.subscribe('273e0008-4c4d-454d-96be-f03bac821358', callback=self._handle_11)

        ### Reciben mucha data por segundo: ## ~17 x seg
        ## handle 0x14
        self.device.subscribe('273e0009-4c4d-454d-96be-f03bac821358', callback=self._handle_14)
        ## handle 0x17
        # self.device.subscribe('273e000a-4c4d-454d-96be-f03bac821358', callback=self._handle_17)


    def _handle_battery(self, handle, data):
        """Handle the battery data"""

        aa = bitstring.Bits(bytes=data)
        pattern = "uint:16,int:16,int:16,int:16,int:16" # The rest is 0 padding
        res = aa.unpack(pattern)

        # El uint:16 de timestamp va avanzando de 1 en 1 --> tiene sentido
        # Los dos uint:16 del final tienen sentido, temperatura y rango de mV

        t = time()
        string_hex = ''.join('{:02x}'.format(x) for x in data)
        string_hex = string_hex[4:] # Quitar tiempo
        self.lista.append([t, *string_hex, *res])

        # self.callback_other(t, res)

        # print(hex(handle))
        # print("bytes: {}".format(len(data)))
        # print("bits: {}".format(len(aa)))
        # print("5 ints: {}".format(res))
        # print("5 ints: {}".format(res2))
        # print(data)
        # print(string_hex)
        # print("-----------------------")

    def _handle_11(self, handle, data):
        """ """

        aa = bitstring.Bits(bytes=data)
        # pattern = "uint:16,uint:12,uint:12,uint:12,uint:12,uint:12,uint:12,uint:12, \
        #             uint:12,uint:12,uint:12,uint:12,uint:12"
        pattern = "uint:16,int:12,int:12,int:12,int:12,int:12,int:12,int:12, \
                    int:12,int:12,int:12,int:12,int:12"

        res = aa.unpack(pattern)

        t = time()

        data = []
        i = 2
        while i < len(res):
            data.append(res[i])
            i += 2


        string_hex = ''.join('{:02x}'.format(x) for x in data)
        string_hex = string_hex[4:]
        self.lista.append([t, *string_hex, *data])

        self.callback_other(t, data)
        # print("handle: {}, {}".format(hex(handle), handle))
        # print("bytes: {}".format(len(data)))
        # print("bits: {}".format(len(aa)))
        # print("parsed: {}".format(res))
        # print(data)
        # print(string_hex) # Juntar todo como string hexadecimal
        # print("-----------------------")
        #
        # print(t)

    def _unpack(self, data):
        """Try to unpack as float from 16bit, zero pad doesnt work """
        zeros = bytearray(b"\x00\x00") # zero padding
        nums = []
        i = 4 # Omitir el timestamp
        while i + 2 < len(data):
            b = struct.unpack('f', zeros + data[i:i+2])
            print(b)
            nums.append(b)
            i += 2

        print(nums)

        return nums

    def _handle_14(self, handle, data):
        """ """

        aa = bitstring.Bits(bytes=data)
        # pattern = "uint:16,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,\
        #             uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8"
        # pattern = "uint:16,int:12,int:12,int:12,int:12,int:12,int:12, \
        #             int:12,int:12,int:12,int:12,int:12,int:12"
        pattern = "uint:16,uint:16,uint:16,uint:16,uint:16,uint:16,uint:16, \
                    uint:16,uint:16,uint:16"
        res = aa.unpack(pattern)

        t = time()
        string_hex = ''.join('{:02x}'.format(x) for x in data)
        string_hex = string_hex[4:] # Quitar tiempo
        string_big = []
        i = 0
        while i + 4 <= len(string_hex):
            string_big.append(string_hex[i:i+4])
            i += 4
        # self.lista.append([t, *string_big, *res])
        self.lista.append([t, aa.bin])

        self.callback_other(t, res[1:])

        # print("handle: {}, {}".format(hex(handle), handle))
        # print("bytes: {}".format(len(data)))
        # print("bits: {}".format(len(aa)))
        # print("parsed: {}".format(res))
        # print(data)
        # print(string_hex) # Juntar todo como string hexadecimal
        # print(string_read) # Pasar a char
        # print("-----------------------")
        #
        # print(t)

    def _handle_17(self, handle, data):
        """ """

        aa = bitstring.Bits(bytes=data)
        # pattern = "uint:16,int:8,int:8,int:8,int:8,int:8,int:8,int:8,int:8,int:8,\
        #             uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8"
        pattern = "uint:16,uint:16,uint:16,uint:16,uint:16,uint:16,uint:16, \
                    uint:16,uint:16,uint:16"
        res = aa.unpack(pattern)

        t = time()
        string_hex = ''.join('{:02x}'.format(x) for x in data)
        string_hex = string_hex[4:] # Quitar tiempo
        self.lista.append([t, *string_hex, *res])

        self.callback_other(t, res[1:])

        # print("handle: {}, {}".format(hex(handle), handle))
        # print("bytes: {}".format(len(data)))
        # print("bits: {}".format(len(aa)))
        # print("parsed: {}".format(res))
        # print(data)
        # print(string_hex) # Juntar todo como string hexadecimal
        # print(string_read) # Pasar a char
        # print("-----------------------")
        #
        # print(t)
