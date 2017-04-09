# Muse player


## Usage

Turn on the muse headband and stream data with python, acts as a server:

`python play.py`

See more options with `python play.py --help`

Get the localhost up, to act as a client:

`python -m http.server 8888`

Put on the headband, go to http://localhost:8888 and visualize the live muse data.

## Requirements
Python 3.5, Muse headband 2016.

Python libraries:
* flask: streams data to js client
