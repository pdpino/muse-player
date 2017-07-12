# Muse player

## This repo has:
* `play.py`, a script to connect to Muse, receive the data, save it and stream it.
* `plotting.py`, a script to plot saved data. It can plot the raw channels and the delta, theta, alpha, beta, gamma waves (developing).
* A webpage to plot the streamed data. See [usage](#usage).



<a name="usage" />

## Usage

### Play
Use `python play.py -s` to connect with the Muse device, save the data to a .csv file and stream it to a web client. See more options with `python play.py --help`.

### Plottting
Use `python plotting.py --raw --waves` to plot the raw data and the waves calculated from the data (in time).

### Webpage
Get the webpage up using: `python -m http.server <port>`, where port is different than the one used to stream the data (see `--port` option in `play.py`). Then go to `http://localhost:<port>` and visualize the live muse data.



## Requirements
Python 3.5, Muse headband 2016.

Python libraries:
* numpy, pandas, matplotlib
* flask, flask_cors: stream data to js client
* pygatt, pexpect: bluetooth connection
* bitstring: unpack bytes


## Acknowledgment
* Muse module: alexandre barachant, muse-lsl (https://github.com/alexandrebarachant/muse-lsl)
