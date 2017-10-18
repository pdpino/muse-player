"""Submodule that provides an engine for the streaming.

There are the following classes in this module:
    - generators: provide a generate() method, which is a generator to yields messages to the stream
    - yielders: extends from generators. They do the actual yielding of the data
    - processors: extends from generators. Do not do the actual yielding, instead contains another generator, which is called when generate() is called

    - buffers: receive muse data and enqueue it. Provide the methods:
        - incoming(timestamp, data)
        - outgoing()

    - collectors: save data received. Provide:
        - collect(data)
        - export(), which return a pd.DataFrame with the data ready to be saved to a file

    - calibrators: see Calibrator class for further explanation

The flow of the engine is the following:
    - Get the incoming data, collect it (save for later use) and buffer it (enqueue)
    - Provide a generator to pass to the stream, which dequeue the data and yields from a generator
    - If the generator is a yielder the data is directly yielded, in a format that usually will be specified in the yielder creation
    - If the generator is a processor, then it process the data in some way (specific by processor), and yields from its inner generator (which again, can be a yielder or a processor)

This flow is useful to chain processors. Examples:
    - To stream the raw eeg, no processing is needed, then the generator is a EEGRawYielder
    - To stream waves, the generator will be a WaveProcessor (apply FT analysis to raw EEG), which have a WaveYielder inside to do the yielding
    - To stream feelings, the generator will be a WaveProcessor with a FeelProcessor (transform frequency analysis in a feeling) inside, which will have a Feeler (can calculate and yield a specific type of feeling) to do the yielding

The processors may have inside calibrators and/or calculators to do the hard work

"""

from .engine import *
from .buffers import *
from .processors import *
from .yielders import *
from .feelers import *
