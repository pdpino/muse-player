# TODOs

## Next
* Do EEG101 course

* Revisar el dict que retorna muse por bluetooth (ver bluetooth section en INFO.md), comparar con section "configuration" en "available data" en pagina de muse.

* Ver video laplacian (para terminar capitulo)

* Revisar codigos sfft y convolute (follow FIXMEs and QUESTIONs; review code from scratch)

* Hacer tests:
  + crear onda con N sinewaves, procesarlas y ver fft.

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

### Accelerometer and other data
* Continue trying to get accelerometer, analyze bytes from handle 14 (run it, save it as csv, decode the bytes in batches of 16bits. (See option of (u)ints and map linearly)
* Try to decompile the library code (libmuse_android.so)

### In `play.py`
* despues de un rato vaciar listas full_data y full_time, se llenan mucho. opcion para guardarlas como dump o no
* handle when muse turns off
* ver cuando se desconecta cliente web?  https://stackoverflow.com/questions/18511119/stop-processing-flask-route-if-request-aborted

### Not urgent
* add parse args to README
* ordenar `develop/info` seccion "headband en estado normal" y "en estado extraño"
