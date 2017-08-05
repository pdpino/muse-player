# Developing Info

## Waves
* Lectures: http://www.mikexcohen.com/lectures.html
* Different waves that you can detect (they are not exclusive, but one may express more than the others)
  + delta (1-4Hz)
  + theta (4-8Hz)
  + alpha (8-13Hz) -- estado relajo
  + beta (13-30Hz) -- estado alerta
  + gamma (30-44Hz)
* Video experimenting with alpha wave, using Muse (2014), eyes closed and opened: https://www.youtube.com/watch?v=pGWHhclDV1c
* Alpha wave increases when the eyes are closed. Even more with the TP9 and TP10, because they are closer to the zone of the brain that handles visual information (occipital lobe?)
* Screenshots of experiment: eyes closed, eyes opened and hypnosis. If not available, screenshots are downloaded in `demos/screenshots/experiment_hypnosis_forum` folder. https://forum.choosemuse.com/t/effect-on-brainwave-when-eyes-are-open/1841

* More info (TODO: read)
  + https://www.scientificamerican.com/article/what-is-the-function-of-t-1997-12-22/
  + https://forum.choosemuse.com/t/learn-more-about-brainwaves/1625/5
  + (referenced by last link) http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0130129

## Headband 2016
* When it is on and disconnected (advertising?) the lights blink rather fast. When connected they blink a bit slower. When streaming data they don't blink at all.

## Data dumps
* dump3 is 10 seconds long: 5 first seconds sitting down quietly; at second 5 stand up and walk.

## MAC Addresses
* MAC de antena bluetooth: 00:1B:DC:06:B1:FB
* MAC de muse: 00:55:DA:B3:20:D7

## Channel order
* 0: TP9 -- behind left ear
* 1: AF7 -- right side forehead
* 2: AF8 -- right side forehead
* 3: TP10 -- behind right ear
* 4: Right AUX -- middle forehead (reference)

## AC power
* Frequency from AC power in: (https://en.wikipedia.org/wiki/Mains_electricity_by_country)   
  + Chile: 50 hz
  + USA: 60 hz
* Consider using a notch filter (band-stop filter) in one of those frequencies


## Datasheet de muse dice que libreria trae:
* raw EEG data
* raw accelerometer data
* raw spectra (delta, theta, alpha, beta, gamma)
* total power
* artifact detection (eye blink, jaw clench)
* Fast Fourier Transform (FFT) coefficients
* experimental brain-state classifiers


## Bluetooth packets (summary)
NOTE: some of the meanings were inflicted from http://developer.choosemuse.com/research-tools/available-data

* You send commands to the 0x000e handle
* Basics:
  - 02:64:0a -- 'd\n' -- Start streaming
  - 02:68:0a -- 'h\n' -- Stop streaming
  - 02:73:0a -- 's\n' -- Return a dict with the configuration (see available-data) -- example:
    + "hn":"Muse-20D7" -- name
    + "sn":"2021-ZXLY-20D7" -- serial number
    + "ma":"00-55-da-b3-20-d7" -- mac address
    + "id":"07473435 32313630 00210042"
    + "bp":88 -- battery percent remaining? if you see it in time, it may be
    + "ts":0
    + "ps":32 -- preset -- value in decimal, transform to hex and you get the Muse preset
    + "rc":0 -- return status, 0: OK, 1: Not OK
  - 03:76:31:0a -- 'v1\n' -- get version data (see available-data) -- example:
    + "ap":"headset"
    + "sp":"RevE"
    + "tp":"consumer" -- firmware type (why so different letters in the key? changed name in muse2016)
    + "hw":"2.1" -- hardware version
    + "bn":27 -- build number
    + "fw":"1.2.13" -- firmware version
    + "bl":"1.2.3" -- boot loader version
    + "pv":1 -- protocol version
    + "rc":0 -- return status
  - 04:70:32:31:0a -- 'p21\n' -- set preset formed by [0x32, 0x31] in ASCII
