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
* flask, flask_cors: stream data to js client
* pygatt: bluetooth connection
* bitstring: unpack bytes


## Acknowledgments
* Muse module: alexandre barachant, muse-lsl (https://github.com/alexandrebarachant/muse-lsl)


## Developing
There are mutiple app_*.js files. Each one of those implements a different library to plot the data.
* app.js: Plotly -- too slow
* app_v2.js: Canvas JS -- slow
* app_v3.js: d3 -- developing
* app_v4.js: rickshaw -- developing
  - necesita d3 v3, v4 cambio API

There are multiple index.html files
* index_v1.html: for every app.js version, except v4 (rickshaw)
* index.html: currently using for rickshaw debugging
