# Developing Info

## Headband 2016
* When it is on and disconnected (advertising?) the lights blink rather fast. When connected they blink a bit slower. When streaming data they don't blink at all.

## Data dumps
* dump3 is 10 seconds long: 5 first seconds sitting down quietly; at second 5 stand up and walk.

## MAC Addresses
* MAC de antena bluetooth: 00:1B:DC:06:B1:FB
* MAC de muse: 00:55:DA:B3:20:D7

## Channel order (segun barachant)
* 0: TP9 -- atrás oreja izquierda
* 1: AF7 -- lado izquierdo frente
* 2: AF8 -- lado derecho frente
* 3: TP10 -- atrás oreja derecha
* 4: Right AUX -- medio frente (reference)

## Datasheet de muse dice que libreria trae:
* raw EEG data
* raw accelerometer data
* raw spectra
    * delta (1-4Hz)
    * theta (4-8Hz)
    * alpha (8-13Hz) -- estado relajo
    * beta (13-30Hz) -- estado alerta
    * gamma (30-44Hz)
* total power
* artifact detection (eye blink, jaw clench)
* Fast Fourier Transform (FFT) coefficients
* experimental brain-state classifiers


## Conclusion on bluetooth packets
* You send commands to the 0x000e handle
* Basics:
  - 02:64:0a -- Start streaming
  - 02:68:0a -- Stop streaming
  - 02:73:0a -- Return a dict with the status (?) -- example:
    + "hn":"Muse-20D7" -- name
    + "sn":"2021-ZXLY-20D7"
    + "ma":"00-55-da-b3-20-d7" -- mac address
    + "id":"07473435 32313630 00210042"
    + "bp":88
    + "ts":0
    + "ps":32 -- preset -- value in decimal, transform to hex and you get the Muse preset
    + "rc":0 -- return status, 0: OK, 1: Not OK
  - 03:76:31:0a -- 'v1' -- get version info? -- example:
    {"ap":"headset","sp":"RevE","tp":"consumer","hw":"2.1","bn":27,"fw":"1.2.13","bl":"1.2.3","pv":1,"rc":0}
  - 04:70:32:31:0a -- 'p21\n' -- set preset formed by [0x32, 0x31] in ASCII

## Examining Bluetooth packets
Examinando packets cuando muse se conecta con app:
- Sent Write Command: (Subscribir al handle 0x000e)
  * handle: 0x000f
  * value?: 0x0001 (Indication: False, Notification: True)

- Sent Write Command:
  * handle: 0x000e
  * value: 03:76:31:0a -- 'v1'

- Receive Handle value: 9 veces, handle: 0x000e, datos (20 bytes c/u):
  * 10:7b:22:61:70:22:3a:22:68:65:61:64:73:65:74:22:2c:00:00:00
  * 0c:22:73:70:22:3a:22:52:65:76:45:22:2c:65:74:22:2c:00:00:00
  * 10:22:74:70:22:3a:22:63:6f:6e:73:75:6d:65:72:22:2c:00:00:00
  * 0b:22:68:77:22:3a:22:32:2e:31:22:2c:6d:65:72:22:2c:00:00:00
  * 08:22:62:6e:22:3a:32:37:2c:31:22:2c:6d:65:72:22:2c:00:00:00
  * 0e:22:66:77:22:3a:22:31:2e:32:2e:31:33:22:2c:22:2c:00:00:00
  * 0d:22:62:6c:22:3a:22:31:2e:32:2e:33:22:2c:2c:22:2c:00:00:00
  * 07:22:70:76:22:3a:31:2c:2e:32:2e:33:22:2c:2c:22:2c:00:00:00
  * 07:22:72:63:22:3a:30:7d:2e:32:2e:33:22:2c:2c:22:2c:00:00:00
  * Meaning: {"ap":"headset","sp":"RevE","tp":"consumer","hw":"2.1","bn":27,"fw":"1.2.13","bl":"1.2.3","pv":1,"rc":0}

- Sent Write Command:
  * handle: 0x000e
  * value: 02730a -- 's' -- 'status?'

- Receive Handle value: 11 veces, handle: 0x000e, datos (20 bytes c/u):
  * 12:7b:22:68:6e:22:3a:22:4d:75:73:65:2d:32:30:44:37:22:2c:00
  * 13:22:73:6e:22:3a:22:32:30:32:31:2d:5a:58:4c:59:2d:32:30:44
  * 03:37:22:2c:22:3a:22:32:30:32:31:2d:5a:58:4c:59:2d:32:30:44
  * 13:22:6d:61:22:3a:22:30:30:2d:35:35:2d:64:61:2d:62:33:2d:32
  * 06:30:2d:64:37:22:2c:30:30:2d:35:35:2d:64:61:2d:62:33:2d:32
  * 13:22:69:64:22:3a:22:30:37:34:37:33:34:33:35:20:33:32:33:31
  * 0f:33:36:33:30:20:30:30:32:31:30:30:34:32:22:2c:33:32:33:31
  * 08:22:62:70:22:3a:38:38:2c:31:30:30:34:32:22:2c:33:32:33:31
  * 07:22:74:73:22:3a:30:2c:2c:31:30:30:34:32:22:2c:33:32:33:31
  * 08:22:70:73:22:3a:33:32:2c:31:30:30:34:32:22:2c:33:32:33:31
  * 07:22:72:63:22:3a:30:7d:2c:31:30:30:34:32:22:2c:33:32:33:31
  * Meaning:
  {"hn":"Muse-20D7","sn":"2021-ZXLY-20D7","ma":"00-55-da-b3-20-d7","id":"07473435 32313630 00210042","bp":88,"ts":0,"ps":32,"rc":0}


- Sent Write Command:
  * handle: 0x000e
  * value: 02680a -- Stop transmitting -- 'h' -- 'halt?'

- Receive Handle value: 1 vez, handle 0x000e, dato:
  * 08:7b:22:72:63:22:3a:30:7d:31:30:30:34:32:22:2c:33:32:33:31 -- {"rc": 0}

- Sent Write Command:
  * handle: 0x000e
  * value: 04:70:32:31:0a -- 'p21' -- 'preset 21?'

- Receive Handle value: 1 vez, handle 0x000e, dato:
  * 08:7b:22:72:63:22:3a:30:7d:31:30:30:34:32:22:2c:33:32:33:31 -- {"rc": 0}

- Sent Write Command:
  * handle: 0x000e
  * value: 02730a -- 's'

- Receive Handle value: 11 veces, handle: 0x000e, datos (20 bytes c/u):
  * 12:7b:22:68:6e:22:3a:22:4d:75:73:65:2d:32:30:44:37:22:2c:31
  * 13:22:73:6e:22:3a:22:32:30:32:31:2d:5a:58:4c:59:2d:32:30:44
  * 03:37:22:2c:22:3a:22:32:30:32:31:2d:5a:58:4c:59:2d:32:30:44
  * 13:22:6d:61:22:3a:22:30:30:2d:35:35:2d:64:61:2d:62:33:2d:32
  * 06:30:2d:64:37:22:2c:30:30:2d:35:35:2d:64:61:2d:62:33:2d:32
  * 13:22:69:64:22:3a:22:30:37:34:37:33:34:33:35:20:33:32:33:31
  * 0f:33:36:33:30:20:30:30:32:31:30:30:34:32:22:2c:33:32:33:31
  * 08:22:62:70:22:3a:38:38:2c:31:30:30:34:32:22:2c:33:32:33:31
  * 07:22:74:73:22:3a:30:2c:2c:31:30:30:34:32:22:2c:33:32:33:31
  * 08:22:70:73:22:3a:33:33:2c:31:30:30:34:32:22:2c:33:32:33:31
  * 07:22:72:63:22:3a:30:7d:2c:31:30:30:34:32:22:2c:33:32:33:31
  * Meaning: {"hn":"Muse-20D7","sn":"2021-ZXLY-20D7","ma":"00-55-da-b3-20-d7","id":"07473435 32313630 00210042","bp":88,"ts":0,"ps":33,"rc":0}

- Sent Write Request: (subscribe, notifications)
  * handle: 0x001e, 0x0021, 0x0024, 0x002a, 0x002d, 0x0012, 0x001b, 0x0018, 0x0015
  * value: 0x01

- Sent Write Command:
  * handle: 0x000e
  * value: 02640a -- Start transmitting -- 'd'

- Receive from handle:
  * handle: 0x000e
  * value: {"rc": 0}

- Receive from handles: 0x14, 0x17, 0x29, 0x26, 0x20, 0x23, 0x11 -- multiple values

- Sent Write Command:
  * handle: 0x000e
  * value: 02680a -- Stop transmitting -- 'h'

- Receive Handle value: 1 vez, handle 0x000e, dato:
  * value: 08:7b:22:72:63:22:3a:30:7d:31:30:30:34:32:22:2c:33:32:33:31 -- {"rc": 0}




## Headband se comporta extraña, probando con gatttool
TODO: ordenar esto

Usando:
```
gatttool -b <MAC> -I # Interactive mode
> connect
> char-read-uuid <value>
```

Formato: num -- bytes -- info
num: numero de handle
bytes: info leida en ese handle
info: mas info de https://www.bluetooth.com/specifications/

* uuid = 2902. Descriptors: client characteristic configuration
4 -- 00 00 -- 00 = 0000 0000
f -- 00 00
2 bytes (16bits) of properties. Format by bit:
  - 0: notifications enabled
  - 1: indications enabled
  - 2-15: reserved for future use


* uuid = 2803. Declaration: GATT Characteristic declaration
2 -- 20 03 00 05 2a -- 20 = 0010 0000 = indication
6 -- 4e 07 00 00 2a -- 4e = 0100 1110 = auth + write + read
8 -- 4e 09 00 01 2a -- 4e = 0100 1110
a -- 0a 0b 00 04 2a -- 0a = 0000 1010 = auth + read
d -- 14 0e 00 58 13 82 ac 3b f0 be 96 4d 45 4d 4c 01 00 3e 27 -- 14 = 0001 0100 = notify + write (sin response)
Format:
byte1: char properties (8bits). Bits:
  - 0: broadcast
  - 1: read
  - 2: write without response
  - 3: write
  - 4: notify
  - 5: indicate
  - 6: auth signed writes
  - 7: extended properties
  - endianess?
byte2-3: characteristic value handle (16bits)
byte4-5-beyond?: characteristic uuid (gatt_uuid)

* uuid = 2800. Declaration: primary service declaration
1 -- 01 18 -- uuid (gatt_uuid type (i assume 16bit))
5 -- 00 18
c -- 8d fe

* uuid = 2a01. Characteristic: appearance
9 -- 00 00 -- unknown (16 bit format)

* uuid = 2A00. Characteristic: device name
7 -- 4d 75 73 65 2d 32 30 44 37 -- chars in utf8

* uuid = 2a04. Characteristic: Peripheral preferred connection parameters
b -- ff ff ff ff 00 00 ff ff -- min conn interval, max conn interval, slave latency, connn superv timeout (each is uint16 (16bits))

* uuid = 2a05. Characteristic: service changed
3 -- cant be read
Can't be read -- start of affected attr handle range, end of affected attr handle range (uint16 each)

* missing:
e -- cant be read

* Probado con:
- todas las uuid de servicios (https://www.bluetooth.com/specifications/gatt/services)
- todas las uuid de caracteristicas (https://www.bluetooth.com/specifications/gatt/characteristics)
- todas las uuid de descriptores (https://www.bluetooth.com/specifications/gatt/descriptors)
- todas las uuid de declaraciones  (https://www.bluetooth.com/specifications/gatt/declarations)




## Headband en estado normal
TODO: ordenar todo

[00:55:DA:B3:20:D7][LE]> characteristics
handle: 0x0002, char properties: 0x20, char value handle: 0x0003, uuid: 00002a05-0000-1000-8000-00805f9b34fb
handle: 0x0006, char properties: 0x4e, char value handle: 0x0007, uuid: 00002a00-0000-1000-8000-00805f9b34fb
handle: 0x0008, char properties: 0x4e, char value handle: 0x0009, uuid: 00002a01-0000-1000-8000-00805f9b34fb
handle: 0x000a, char properties: 0x0a, char value handle: 0x000b, uuid: 00002a04-0000-1000-8000-00805f9b34fb
handle: 0x000d, char properties: 0x14, char value handle: 0x000e, uuid: 273e0001-4c4d-454d-96be-f03bac821358
handle: 0x0010, char properties: 0x10, char value handle: 0x0011, uuid: 273e0008-4c4d-454d-96be-f03bac821358
handle: 0x0013, char properties: 0x10, char value handle: 0x0014, uuid: 273e0009-4c4d-454d-96be-f03bac821358
handle: 0x0016, char properties: 0x10, char value handle: 0x0017, uuid: 273e000a-4c4d-454d-96be-f03bac821358
handle: 0x0019, char properties: 0x10, char value handle: 0x001a, uuid: 273e000b-4c4d-454d-96be-f03bac821358
handle: 0x001c, char properties: 0x10, char value handle: 0x001d, uuid: 273e0002-4c4d-454d-96be-f03bac821358
handle: 0x001f, char properties: 0x10, char value handle: 0x0020, uuid: 273e0003-4c4d-454d-96be-f03bac821358
handle: 0x0022, char properties: 0x10, char value handle: 0x0023, uuid: 273e0004-4c4d-454d-96be-f03bac821358
handle: 0x0025, char properties: 0x10, char value handle: 0x0026, uuid: 273e0005-4c4d-454d-96be-f03bac821358
handle: 0x0028, char properties: 0x10, char value handle: 0x0029, uuid: 273e0006-4c4d-454d-96be-f03bac821358
handle: 0x002b, char properties: 0x10, char value handle: 0x002c, uuid: 273e0007-4c4d-454d-96be-f03bac821358
[00:55:DA:B3:20:D7][LE]> primary
attr handle: 0x0001, end grp handle: 0x0004 uuid: 00001801-0000-1000-8000-00805f9b34fb
attr handle: 0x0005, end grp handle: 0x000b uuid: 00001800-0000-1000-8000-00805f9b34fb
attr handle: 0x000c, end grp handle: 0x002d uuid: 0000fe8d-0000-1000-8000-00805f9b34fb
[00:55:DA:B3:20:D7][LE]> char-desc
handle: 0x0001, uuid: 00002800-0000-1000-8000-00805f9b34fb
handle: 0x0002, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0003, uuid: 00002a05-0000-1000-8000-00805f9b34fb
handle: 0x0004, uuid: 00002902-0000-1000-8000-00805f9b34fb
handle: 0x0005, uuid: 00002800-0000-1000-8000-00805f9b34fb
handle: 0x0006, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0007, uuid: 00002a00-0000-1000-8000-00805f9b34fb
handle: 0x0008, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0009, uuid: 00002a01-0000-1000-8000-00805f9b34fb
handle: 0x000a, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x000b, uuid: 00002a04-0000-1000-8000-00805f9b34fb
handle: 0x000c, uuid: 00002800-0000-1000-8000-00805f9b34fb
handle: 0x000d, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x000e, uuid: 273e0001-4c4d-454d-96be-f03bac821358
handle: 0x000f, uuid: 00002902-0000-1000-8000-00805f9b34fb
handle: 0x0010, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0011, uuid: 273e0008-4c4d-454d-96be-f03bac821358
handle: 0x0012, uuid: 00002902-0000-1000-8000-00805f9b34fb
handle: 0x0013, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0014, uuid: 273e0009-4c4d-454d-96be-f03bac821358
handle: 0x0015, uuid: 00002902-0000-1000-8000-00805f9b34fb
handle: 0x0016, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0017, uuid: 273e000a-4c4d-454d-96be-f03bac821358
handle: 0x0018, uuid: 00002902-0000-1000-8000-00805f9b34fb
handle: 0x0019, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x001a, uuid: 273e000b-4c4d-454d-96be-f03bac821358
handle: 0x001b, uuid: 00002902-0000-1000-8000-00805f9b34fb
handle: 0x001c, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x001d, uuid: 273e0002-4c4d-454d-96be-f03bac821358
handle: 0x001e, uuid: 00002902-0000-1000-8000-00805f9b34fb
handle: 0x001f, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0020, uuid: 273e0003-4c4d-454d-96be-f03bac821358
handle: 0x0021, uuid: 00002902-0000-1000-8000-00805f9b34fb
handle: 0x0022, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0023, uuid: 273e0004-4c4d-454d-96be-f03bac821358
handle: 0x0024, uuid: 00002902-0000-1000-8000-00805f9b34fb
handle: 0x0025, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0026, uuid: 273e0005-4c4d-454d-96be-f03bac821358
handle: 0x0027, uuid: 00002902-0000-1000-8000-00805f9b34fb
handle: 0x0028, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0029, uuid: 273e0006-4c4d-454d-96be-f03bac821358
handle: 0x002a, uuid: 00002902-0000-1000-8000-00805f9b34fb
handle: 0x002b, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x002c, uuid: 273e0007-4c4d-454d-96be-f03bac821358
handle: 0x002d, uuid: 00002902-0000-1000-8000-00805f9b34fb
