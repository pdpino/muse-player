# TODOs

Sections:
* Whole project
* Software/Code
  - Streamer server (`play.py`)
  - Javascript client (`app.js`)
  - Offline analysis
  - EEG data
  - Muse driver
  - Classes and books
  - Conventions, documentation and others

Usual subsections for code:
* Pending
* Refactors
* Next
* Wishlist

***

## Project
### Refactors
* Refactor filesys
* Refactor yielders?
* Comply with moodplay format in yielders

### Pending
* Improve Muse module + PR barachant repo

### Next
* Artifact removal in real time
  - search/read papers
* Email evic people

### Others (old)
* Order offline tools, prepare pipeline to receive data, apply formulas, show results
* Prepare user protocol
* Update README with current tools
* muse-direct

## Software

#### Server, play.py
* REVIEW architecture! should the server work without the need of a client making a request? (currently this activates the generator)
* (Depends on moodplay) use Formatter to yield things, comply with moodplay standards to send JSON
* Consider moving the time normalization to the engine, so no one else has to handle it
* Design calibrators
  - Consider an option to reset calibrators

* Pending:
  - Add stream mode configuration for waves (select channel)
  - Check TODOs and REVIEWs in code
* Refactors:
  - `arr_freqs` is in many places in wave yielding (in `play.py`)
  - Move configuration of streaming to objects or functions (in `play.py`)
  - Separate `tf` in submodules (`convolution`, `sttft` and `common`)
  - In `buffers`: evaluate changing deque to queue (used for messaging between threads, is already thread-safe?)
* Next:
  - Send marks to the client
* Wishlist:
  - Architecture to save dumps to not overload memory
  - make 2 calibrations with one command
  - handle when muse turns off
  - Catch when web client gets disconnected? https://stackoverflow.com/questions/18511119/stop-processing-flask-route-if-request-aborted

#### Client, app.js
* Pending:
  - `TimeChart` class should create html elements for the axis buttons
  - `TimeChart` class should listen to scrolling to change zoom in graph
  - `Connection` class should create html elements for the conn status
* Next:
  - add marks in time (mark message)

#### Offline analysis and tools
* Refactors:
  - two main scripts: `analyze` and `plot`. The first makes all the calculations and the second makes the plots.
* Pending:
  - add axis label for colour in contourplot
* Wishlist:
  - Enable toggle visibility in plots

#### EEG data
* Pre-process (before TF analysis)
  + Notch filter in 50Hz
  + high-pass filter at 0.5 or 1Hz ???
  + ignore data over 100uV (noise)
* Ideas:
  + Review EEG101 course source code (https://github.com/NeuroTechX/eeg-101), search for filters to data coming from muse

#### Muse driver
* Accelerometer and other data. What to do? Options:
  - decompile library code (`libmuse_android.so`)
  - analyze bytes from handle 14, decode in different formats (uint12, float16, etc)
  - map linearly from (u)ints to a certain space, e.g. [0, 1]. That way you see the fluctuation of the value. If it makes sense, this may be the transformation used by muse
  - In the battery data, compare the value from one of the handles subscribed to the returned by muse when asked for the status (see INFO, bluetooth packets, key="bp")

#### Classes and books
* Watch laplacian video (to end chapter)

#### Conventions, documentation and others
* Document engine and processors classes (and interfaces?)
* Change feeling name by something more precise (mood, emotion, etc)
* Define convention for valence-arousal or arousal-valence (same goes for relaxation-concentration)
* add parse args to README
* Order `develop/info`, section "headband en estado normal" and "en estado extraño"
* Move parsers to `frontend/` ??
