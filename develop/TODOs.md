# TODOs

### Waves
* Seguir viendo lectures, viene la 26.

* Move wave functions to `backend/analyze`
* Change `compute_feature_vector`:
  + delete `plot_window` debug option
  + Leave hamming window, remove use of no tapering window
  + don't add (or mean, or etc) bands (alpha, beta, etc)
  + return power in freq and in time
* Make function to plot contour (heat map): freq vs time vs power
* Make function to obtain freq with morlet wavelet convolution

### Accelerometer ant other data
* Continue trying to get accelerometer, analyze bytes from handle 14 (run it, save it as csv, decode the bytes in batches of 16bits.
Try to decompile the library code (libmuse_android.so)

### Others
* despues de un rato vaciar listas full_data y full_time, se llenan mucho. opcion para guardarlas como dump o no
* handle when muse turns off
* ver cuando se desconecta cliente web?  https://stackoverflow.com/questions/18511119/stop-processing-flask-route-if-request-aborted

### Not urgent
* add parse args to README
* ordenar `develop/info` seccion "headband en estado normal" y "en estado extraño"
