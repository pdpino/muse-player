# TODOs

Sections:
* Whole project
* Software/Code
  - Streamer server (`play.py`)
  - Javascript client (`app.js`)
  - Offline analysis
  - EEG data
  - Classes and books
  - Conventions, documentation and others

Usual subsections for code:
* Pending
* Refactors
* Next
* Wishlist

***

## Project

* Artifact removal (offline; real time?)
  - read info on topoplots, which colors are the most important? (most positives or most negatives?), what happens if I multiply by -1 !!
  - check that the mixing is well done

* Show all data in Js client (acc, gyro, battery, etc)
  - refactor player to send better
  - design interface
  - decode bluetooth channels left
  - be sure of acc and gyro data (play with muse direct, wireshark!)

* Email evic people
* Order offline tools, prepare pipeline to receive data, apply formulas, show results
* Prepare user protocol
* Update README with current tools
* muse-direct

## Software

#### Pending
* FIXME: js client has NaN error in d3, only with the first of the graph, only the first time that it connects to the server
* Refactor calibrators and accumulators, design first

#### Server, play.py
* REVIEW architecture! should the server work without the need of a client making a request? (currently this activates the generator)

* Pending:
  - Add stream mode configuration for waves (select channel, select waves is done)

* Refactors:
  - Refactor src/ to fix relative imports
  - `arr_freqs` is in many places in wave yielding (in `play.py`)
  - Move configuration of streaming to objects or functions (in `play.py`)
  - Separate `tf` in submodules (`convolution`, `sttft` and `common`)
  - In `buffers`: evaluate changing deque to queue (used for messaging between threads, is already thread-safe?)

* Next:
  - Send marks to the client (after the refactor should be easy)

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
  + ignore data over 100uV (noise) ?
* Ideas:
  + Review EEG101 course source code (https://github.com/NeuroTechX/eeg-101), search for filters to data coming from muse

#### Classes and books
* Watch laplacian video (to end the chapter)

#### Conventions, documentation and others
* Document engine and processors classes (and interfaces?)
* Change feeling name by something more precise (mood, emotion, etc)
* Define convention for valence-arousal or arousal-valence (same goes for relaxation-concentration)
* add parse args to README
* Order `develop/info`, section "headband en estado normal" and "en estado extraño"
* Move parsers to `frontend/` ??
