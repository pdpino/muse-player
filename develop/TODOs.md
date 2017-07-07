# TODOs

## Urgent
* Continue trying to get accelerometer, analyze bytes from handle 14 (run it, save it as csv, decode the bytes in batches of 16bits (docs says 16bits), int? uint? float?, to decode as float16 you need python 3.6)

## Next
* handle when muse turns off
* despues de un rato vaciar listas full_data y full_time, se llenan mucho. opcion para guardarlas como dump o no
* ver cuando se desconecta cliente web.  https://stackoverflow.com/questions/18511119/stop-processing-flask-route-if-request-aborted
* probar qué tanta información se pierde en mandar promedio, un dato o todos. calcular cov o dispersion de 12 samples (?)

## Not urgent
* add parse args to README
* ordenar `develop/info` seccion "headband en estado normal" y "en estado extraño"
