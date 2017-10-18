# TODOs

## Player
* (1) REFACTOR: create signals object that handles calling an action, printing and returning a message for each action
* handle when muse turns off

#### Refactors
* arr_freqs is in many places in wave yielding
* Check TODOs and REVIEWs in code
* Move configuration of streaming to objects or functions

#### Enable more options
* Add stream mode configuration for waves (select channel)

## App.js
* (1) Webpage changes y axis limits in function of new data
  - be careful to not be moving axis all the time: (something like) only every few times decrease limits, increase always, set a inferior limit
* Rename `Graph` to `TimeChart`
* Separate in multiple files
* `Graph` class should create html elements for the axis buttons
* `Graph` class should listen to scrolling to change zoom in graph

* `Connection` class should create html elements for the conn status
* add marks in time (mark message)

## Conventions and documentation
* Document engine and processors classes
* Change feeling name by something more precise
* Define convention for valence-arousal or arousal-valence

## Backend
* Separate tf in submodules (convolution, sttft and common)

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

### Other's others
* add parse args to README
* Order `develop/info`, section "headband en estado normal" and "en estado extraño"
* Move parsers to `frontend/` ??
