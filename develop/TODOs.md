# TODOs

## Next
* Revisar codigos sfft y convolute (follow FIXMEs and QUESTIONs; review code from scratch)

* Fix normalization

* Ver video laplacian (para terminar capitulo)

* Ver links de mail


#### Review raw eeg
* Normalization (in muse module), etc

#### Review wave code
* Review `ssfft`. Review the way to obtain `n_freqs` (see videos).
* Review `convolute` code.


#### Testing
* Multiple tries, closing and opening eyes.
* In `play.py`: implement marks in time (not necessary, but useful)



## Others
* Play with waves: See barachant code (P300)
* Review EEG101 course source code (https://github.com/NeuroTechX/eeg-101), search for filters to data coming from muse

### Accelerometer and other data
* Options:
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
