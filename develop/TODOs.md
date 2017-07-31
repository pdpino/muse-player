# TODOs

### Junta denis, lo que viene:
* marks in time
* review and fix FT code
* baseline and normalization
* accelerometer, decompile library

### Waves
* In `ssfft`, review the way to obtain `n_freqs` (see videos).
* Review `convolute` code.

* See barachant code

* Seguir con capitulo de post-process


### Accelerometer ant other data
* Continue trying to get accelerometer, analyze bytes from handle 14 (run it, save it as csv, decode the bytes in batches of 16bits.
Try to decompile the library code (libmuse_android.so)

### In `play.py`
* Implement marks in time
* despues de un rato vaciar listas full_data y full_time, se llenan mucho. opcion para guardarlas como dump o no
* handle when muse turns off
* ver cuando se desconecta cliente web?  https://stackoverflow.com/questions/18511119/stop-processing-flask-route-if-request-aborted

### Not urgent
* add parse args to README
* ordenar `develop/info` seccion "headband en estado normal" y "en estado extraño"
