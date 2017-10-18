# TODOs

## Next

* Use formula of arousal, valence to calculate feelings

* Move configuration of streaming to objects or functions

* Check TODOs and REVIEWs in code
* Webpage changes y axis limits in function of new data
  - be careful to not be moving axis all the time: (something like) only every few times decrease limits, increase always, set a inferior limit

* Change feeling name by something more precise
* Document engine and processors classes


* Order TODOs



## Others:

### Client: Webpage
* add axis labels
* add marks in time (mark message)
* Change variable names in `app.js` to CamelCase
* `Connection` class should create html elements for the conn status
* `Graph` class should create html elements for the axis buttons
* `Graph` class should listen to scrolling to change zoom in graph
* Prettier header and footer
*

### Server: Python
* Separate tf in submodules (convolution, sttft and common)
* handle when muse turns off

#### In `backend.buffers`:
* Evaluate changing deque to queue (used for messaging between threads)
* After a while dump lists `full_data` and `full_time`, they may use way too much space. Also add option to enable/disable this?

#### Python offline plots
* Enable toggle visibility in plots
* add axis label for colour in contourplot

#### EEG data
* Pre-process (before TF analysis)
  + Notch filter in 50Hz
  + high-pass filter at 0.5 or 1Hz ???
* Ideas:
  + Review EEG101 course source code (https://github.com/NeuroTechX/eeg-101), search for filters to data coming from muse

#### Accelerometer and other data
* What to do? Options:
  + decompile library code (libmuse_android.so)
  + analyze bytes from handle 14, decode in different formats (uint12, float16, etc)
  + map linearly from (u)ints to a certain space, e.g. [0, 1]. That way you see the fluctuation of the value. If it makes sense, this may be the transformation used by muse
  + In the battery data, compare the value from one of the handles subscribed to the returned by muse when asked for the status (see INFO, bluetooth packets, key="bp")

## Others

### Connection between python and client
* Catch when web client gets disconnected? https://stackoverflow.com/questions/18511119/stop-processing-flask-route-if-request-aborted

### Learn
* Watch laplacian video (to end chapter)
* See links in mail (sent to yourself)


### Not urgent
* add parse args to README
* Order `develop/info`, section "headband en estado normal" and "en estado extraño"
* Move parsers to `frontend/` ??
