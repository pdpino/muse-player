# Muse player

## This repo has:
* `play.py`, a script to connect to Muse, receive the data, save it and stream it.
* `analyze.py`, a script to plot saved data. It can plot the raw channels and the delta, theta, alpha, beta, gamma waves (developing).
* A webpage to plot the streamed data. See [usage](#usage).



<a name="usage" />

## Usage

### Play
Use `python play.py` to connect with the Muse device. Options:
* `--save` to save to a csv. Specify the filename with `-f`.
* `--stream` to stream to the web client. If also `-w`, then the alpha, beta, etc waves are streamed. Else, the raw eeg.

When running you can enter messages:
* Special commands start with `-`:
  + `-c` (config): send a command to muse so the configuration information is returned.
  + `-s` (start): start recording a baseline to calibrate the data. It is recommended that the user is still while this is done. A couple of seconds is enough data.
  + `-h` (halt): stop recoding the baseline.
* Any other string is saved as a mark in time. For instance, you could mark when the person started and stopped doing something. Consider:
  + when the person start use any string, like 'reading'. When the person finishes reading, use 'stop reading' or just 'stop'. Only use the word stop in such way (not for a regular mark).

### Analyze
See `python analyze.py --help`.

### Webpage
Get the webpage up using: `python -m http.server <port>`, where port is different than the one used to stream the data (see `--port` option in `play.py`). 8888 is recommended. Then go to `http://localhost:<port>` and visualize the live muse data.



## Requirements
Python 3.5, Muse headband 2016.

### With pip:
`pip install -r develop/requirements.txt`

You may also need to install the `TKinter` package for python3. In ubuntu this is done with:
`sudo apt install python3-tk`


Used python libraries (all installed with pip):
* numpy, pandas, matplotlib
* flask, flask_cors: stream data to js client
* pygatt, pexpect: bluetooth connection
* bitstring: unpack bytes



## Acknowledgment
* Muse module: alexandre barachant, muse-lsl (https://github.com/alexandrebarachant/muse-lsl)
