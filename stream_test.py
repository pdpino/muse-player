#!/usr/bin/env python
"""Script to stream dummy data."""

from time import sleep, time
import pandas as pd
import argparse
import threading
from flask import Response, Flask   # Stream data to client
from flask_cors import CORS
from muse import Muse
import basic
from backend import parsers, data, engine, info

def main():
    data_buffer = engine.DummyBuffer(name="testing")

    # Flask app
    app = Flask(__name__) # iniciar app de Flask
    CORS(app) # para que cliente pueda acceder a este puerto

    # Thread
    stream = threading.Thread(target=app.run, kwargs={"host":'localhost', "port":8889})
    stream.daemon = True

    # Connect data to send
    @app.route('/testing')
    def stream_eeg():
        """Stream the eeg data."""
        return Response(data_buffer.data_generator(), mimetype="text/event-stream")

    stream.start()

    while True:
        try:
            pass
        except:
            print("Interrupted")

    return 0


if __name__ == "__main__":
    main()
