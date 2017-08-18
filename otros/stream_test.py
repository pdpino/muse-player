#!/usr/bin/env python
"""Script to stream dummy data."""

from flask import Response, Flask   # Stream data to client
from flask_cors import CORS

def main():
    # Flask app
    app = Flask(__name__) # iniciar app de Flask
    CORS(app) # para que cliente pueda acceder a este puerto


    # Connect data to send
    @app.route('/testing')
    def stream_eeg():
        """Stream the eeg data."""
        def data_generator():
            while True:
                yield "data: 0\n\n"
        return Response(data_generator(), mimetype="text/event-stream")

    app.run(host='localhost', port=8889)

    return 0


if __name__ == "__main__":
    main()
