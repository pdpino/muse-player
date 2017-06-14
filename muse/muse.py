from time import time, sleep
from sys import platform
import numpy as np
import bitstring
import pygatt
import threading


class Muse():
    """Muse 2016 headband"""

    def __init__(self, address, callback, info=True, eeg=True, other=True, accelero=False,
                 giro=False, norm_factor=None, norm_sub=None):
        """Initialize

        Parameters:
        address --
        callback --
        info -- bool, subscribe to info messages from muse
        eeg -- bool, subscribe to eeg streaming
        accelero -- bool, subscribe to accelerometer messages
        giro -- bool, subscribe to giroscope messages
        norm_factor -- Normalize factor. The eeg data is multiplied by this value, after substracting norm_sub
        norm_sub -- Normalize substractor. The eeg data gets this value substracted
        """


        self.address = address
        self.callback = callback
        self.info = info
        self.other = other
        self.eeg = eeg
        self.accelero = accelero
        self.giro = giro
        self.norm_factor = 0.48828125 if norm_factor is None else norm_factor # default values used by barachant
        self.norm_sub = 2048 if norm_sub is None else norm_sub # default values used by barachant

        # To handle info messages
        self._msgs = [] # Info messages # Each is a string encoding a dict (key, value pairs)
        self._msgs_codes = [] # Initial number that comes in the messages # For each message there is a list of error codes

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
        try:
            self.device = self.adapter.connect(self.address)
        except Exception as e:
            raise(ConnectionError("Can't connect to Muse headband"))


        # Subscribe to messages
        if self.info:
            self._subscribe_admin()

        # Subscribe to other # DEBUG
        if self.other:
            self._subscribe_other()

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
            # 0x70: p
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



    """Printing methods"""

    def _print_msg(self, codes, msg):
        print("\tcodes: {}".format(codes))
        print("\tmsg: {}".format(msg))

    def print_msgs(self):
        """Print the messages received so far.

        It is not thread safe"""

        with self._lock_msg:
            n = len(self._msgs)
            print("There are {} messages:".format(n))
            for i in range(n):
                self._print_msg(self._msgs_codes[i], self._msgs[i])

        return

    def print_last_msg(self, incoming=False):
        """Print the last message received

        Parameters:
        incoming -- bool, if True, try to print the still incoming message. If there isn't one or False, print the last saved"""

        with self._lock_msg:
            if incoming:
                if len(self._current_msg) > 0: # There is an incoming message
                    self._print_msg(self._current_codes, self._current_msg)
                    return

            # Print the last saved message
            if len(self._msgs) == 0:
                print("There are no messages")
                return
            self._print_msg(self._msgs_codes[-1], self._msg[-1])

        return



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
        # data = 0.48828125 * (np.array(data) - 2048) # in microVolts # default value chosen by the autor # QUESTION: why?
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
        tm, d = self._unpack_eeg_channel(data)
        self.data[index] = d
        self.timestamps[index] = timestamp

        if handle == 35: # last data received
            # affect as timestamps the first timestamps - 12 sample
            timestamps = np.arange(-12, 0) / 256.
            timestamps += np.min(self.timestamps)
            self.callback(timestamps, self.data)
            self._init_sample()


    """Handle Admin msg methods"""

    def _subscribe_admin(self):
        """Subscribe to administrative channels."""
        self.device.subscribe('273e0001-4c4d-454d-96be-f03bac821358', callback=self._handle_messages)

    def _init_msg(self):
        """Reset the current msg storage"""
        with self._lock_msg:
            self._current_msg = ""
            self._current_codes = []

    def _handle_messages(self, handle, data):
        """Handle the incoming messages from the 0x000e handle"""

        if handle != 14:
            # Mensajes tienen que llegar de ese handle
            return

        # Decodificar data
        aa = bitstring.Bits(bytes=data)
        pattern = "uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8, \
                    uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8" # Vienen en chars
        res = aa.unpack(pattern)

        # Guardar numero inicial
        with self._lock_msg:
            self._current_codes.append(res[0])

        # Recorrer numeros siguientes
        for a in res[1:]:
            c = chr(a)

            with self._lock_msg:
                self._current_msg += c

            if c == ',': # Esta data termino
                break

            if c == '}': # Msg termino completo
                with self._lock_msg:
                    self._msgs.append(self._current_msg)
                    self._msgs_codes.append(self._current_codes)

                self._init_msg()
                break


    """Handle other"""
    def _subscribe_other(self):
        # DEBUG:

        ### Recibe data cada 10 segundos
        ### Handle: 0x1a = 26 # Le llegan 160 bits, sera la bateria?
        self.device.subscribe('273e000b-4c4d-454d-96be-f03bac821358',
                              callback=self._handle_battery)

        ### No recibe data:
        # handle 0x1d
        # self.device.subscribe('273e0002-4c4d-454d-96be-f03bac821358',
        #                       callback=self.handle_something)


        ### Recibe 4-5 veces por segundo # handle 0x11
        # self.device.subscribe('273e0008-4c4d-454d-96be-f03bac821358',
        #                       callback=self._handle_11)

        ### Reciben mucha data por segundo:
        ## ~17 x seg # handle 0x14
        # self.device.subscribe('273e0009-4c4d-454d-96be-f03bac821358',
        #                       callback=self._handle_14)
        ## ~17 x seg # handle 0x17
        # self.device.subscribe('273e000a-4c4d-454d-96be-f03bac821358',
        #                       callback=self._handle_17)


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
        # pattern = "uint:16,uint:16,uint:16,uint:16,uint:16,uint:16,uint:16, \
        #             uint:16,uint:16,uint:16"
        pattern = "uint:16,uint:12,uint:12,uint:12,uint:12,uint:12,uint:12,uint:12\
                    ,uint:12,uint:12,uint:12,uint:12,uint:12"
        res = aa.unpack(pattern)

        t = time()
        string_hex = ''.join('{:02x}'.format(x) for x in data)
        self.lista.append([t, string_hex, *res])

        # print("handle: {}, {}".format(hex(handle), handle))
        # print("bytes: {}".format(len(data)))
        # print("bits: {}".format(len(aa)))
        # print("parsed: {}".format(res))
        # print(data)
        # print(string_hex) # Juntar todo como string hexadecimal
        # print("-----------------------")
        #
        # print(t)

    def _handle_14(self, handle, data):
        """ """

        aa = bitstring.Bits(bytes=data)
        # pattern = "uint:16,uint:16,uint:16,uint:16,uint:16,uint:16,uint:16, \
        #             uint:16,uint:16,uint:16"
        pattern = "uint:16,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,\
                    uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8"
        res = aa.unpack(pattern)

        t = time()
        string_hex = ''.join('{:02x}'.format(x) for x in data)
        string_hex = string_hex[4:] # Quitar tiempo
        self.lista.append([t, string_hex, *res])

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
        # pattern = "uint:16,uint:16,uint:16,uint:16,uint:16,uint:16,uint:16, \
        #             uint:16,uint:16,uint:16"
        pattern = "uint:16,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,\
                    uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8,uint:8"
        res = aa.unpack(pattern)

        t = time()
        string_hex = ''.join('{:02x}'.format(x) for x in data)
        string_hex = string_hex[4:] # Quitar tiempo
        self.lista.append([t, string_hex, *res])

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
