# TODOs

## Next

#### Testing
* Play with waves: See barachant code (P300)
* Play with parameters in both methods

#### Learn
* Ver video laplacian (para terminar capitulo)
* Ver links de mail

#### Pre-process (before TF analysis)
* Notch filter in 50Hz
* high-pass filter at 0.5 or 1Hz ???

#### Post-process (after TF analysis)
* when normalizing: add parameters to set the time window to use as Baseline (now is hardcoded)


## Others
* Use a first message from server defining the type of data that will be sent (EEG or Waves). Then the client js changes the Graph accordingly
* Separate tf in submodules (convolution, sttft and common)
* Evaluate changing deque to queue (used for messaging between threads)
* Review EEG101 course source code (https://github.com/NeuroTechX/eeg-101), search for filters to data coming from muse
* Python is streaming wrong one time? sending 5 elements instead of 6 (time + channels)

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
