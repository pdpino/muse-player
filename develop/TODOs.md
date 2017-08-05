# TODOs

## Next
#### Testing
* Test closing eyes, eyes open, etc
* Implement marks in time (in play)
* Play with parameters in both methods

#### Post-process (after TF analysis)
* Fix normalization

#### Learn
* Ver video laplacian (para terminar capitulo)
* Ver links de mail

#### Pre-process (before TF analysis)
* Notch filter in 50Hz
* high-pass filter at 0.5 or 1Hz ???


## Others
* In `analyze.py`
  + move `load_data()` to backend and move `raw` option to another script (`plot_raw.py`)
  + merge `test.py` into `analyze.py` (the parameters are very similar)
* Play with waves: See barachant code (P300)
* Review EEG101 course source code (https://github.com/NeuroTechX/eeg-101), search for filters to data coming from muse

### Accelerometer and other data
* With messages in Muse only habilitate option to print them push, not send them back to main.
* What to do? Options:
  + decompile library code (libmuse_android.so)
  + analyze bytes from handle 14, decode in different formats (uint12, float16, etc)
  + map linearly from (u)ints to a certain space, e.g. [0, 1]. That way you see the fluctuation of the value. If it makes sense, this may be the transformation used by muse
  + In the battery data, compare the value from one of the handles subscribed to the returned by muse when asked for the status (see INFO, bluetooth packets, key="bp")

### In `play.py`
* despues de un rato vaciar listas full_data y full_time, se llenan mucho. opcion para guardarlas como dump o no
* handle when muse turns off
* ver cuando se desconecta cliente web?  https://stackoverflow.com/questions/18511119/stop-processing-flask-route-if-request-aborted

### Not urgent
* add parse args to README
* ordenar `develop/info` seccion "headband en estado normal" y "en estado extraño"
