# TODOs

## Next
* Play with waves: See barachant code (P300)

#### Testing
* Play with parameters in both methods

#### Learn
* Ver video laplacian (para terminar capitulo)
* Ver links de mail

#### Pre-process (before TF analysis)
* Notch filter in 50Hz
* high-pass filter at 0.5 or 1Hz ???

#### Post-process (after TF analysis)
* when normalizing: add parameters to set the time window to use as Baseline


## Others
* Review EEG101 course source code (https://github.com/NeuroTechX/eeg-101), search for filters to data coming from muse
* Question: is normalizing OK?

### Accelerometer and other data
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
