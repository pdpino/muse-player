#!/usr/bin/env python
"""Script to stream dummy data."""
from time import sleep
from flask import Response, Flask   # Stream data to client
from flask_cors import CORS
import numpy as np

def main():
    # Flask app
    app = Flask(__name__) # iniciar app de Flask
    CORS(app) # para que cliente pueda acceder a este puerto

    # Connect data to send
    @app.route('/data/muse')
    def stream_test_data():
        """Stream dummy data."""
        # Parameters # TASK: use argparse
        n_data = 5 # not counting time
        sleep_time = 0.2
        max_num = 100

        # Create string to format
        str_stream = "data: {}" + ", {}" * n_data + "\n\n"

        def data_generator():
            seconds = 0
            while True:
                data = np.random.sample(n_data) * max_num
                yield str_stream.format(seconds, *data)
                sleep(sleep_time)
                seconds += sleep_time

        return Response(data_generator(), mimetype="text/event-stream")

    app.run(host='localhost', port=8889)

    return 0


if __name__ == "__main__":
    main()
