# Developing Info

## Headband 2016
* When it is on and disconnected (advertising?) the lights blink rather fast. When connected they blink a bit slower. When streaming data they don't blink at all.

## MAC Addresses
* MAC de antena bluetooth: 00:1B:DC:06:B1:FB
* MAC de muse: 00:55:DA:B3:20:D7

## Channel order (segun barachant)
* 0: TP9
* 1: AF7
* 2: AF8
* 3: TP10
* 4: Right AUX

* Resto???

## js old files
In the old/ folder (may not be up in the repo) there are mutiple app_*.js files. Each one of those is a different implementation to plot the data.
* app_v1.js: Plotly -- too slow
* app_v2.js: Canvas JS -- slow
* app_v3.js: d3 v3
* app_v4.js: d3 v4
* app_v5.js: rickshaw
* app_v6.js: d3 v3 -- the best -- version actual app.js



## Headband extraña, probando con gatttool
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
[00:55:DA:B3:20:D7][LE]> primary
attr handle: 0x0001, end grp handle: 0x0004 uuid: 00001801-0000-1000-8000-00805f9b34fb
attr handle: 0x0005, end grp handle: 0x000b uuid: 00001800-0000-1000-8000-00805f9b34fb
attr handle: 0x000c, end grp handle: 0x002d uuid: 0000fe8d-0000-1000-8000-00805f9b34fb
[00:55:DA:B3:20:D7][LE]>
