# Muse player

## Requirements
* Python 3.5, Muse headband 2016.
* Python libs: `pip install -r requirements.txt`
* You may also need to install the `TKinter` package for python3, to use
`matplotlib`. In ubuntu this is done with: `sudo apt install python3-tk`


## Player usage

### Run server
Use `python play.py` to connect with the Muse device and setup the server.
Some options:
* `--stream` to select what to stream to the web interface,
  one of: `eeg`, `waves`, `feel`, `feel_val_aro`, `lz`.
* `--faker` to generate fake data instead of using the muse device. Useful
  for testing.

Example:
`python play.py --faker --stream eeg`

See all the options with `--help`.


### Run client
Get the webpage up with: `python -m http.server <port>`, with some port chosen,
e.g. 8000.
This port must be different from the one in `play.py --port`.
Then go to `http://localhost:<port>` and visualize the live muse data.


### Marks (in server)
When running the server marks can be saved in time:
* Type any string in the terminal and hit enter. Example: 'started reading',
  'finished reading'.
* Some special commands (needs `--control` option present):
  + `-c` (config) or `-v` (version): sends a command to retrieve configuration
  information from the muse device.
  + `-1`, `-2`, `-3`, `-4`: start and end recording baselines. Depends on the
  stream configuration.



## Analyze data
See `python analyze.py --help`.


## Acknowledgment
* Muse module: alexandre barachant, muse-lsl (https://github.com/alexandrebarachant/muse-lsl)
