#!/usr/bin/env python
"""Stream random simulated eeg data to client, used for debugging"""

from time import sleep, time
from collections import deque
import numpy as np
import argparse
import threading
import signal
from flask import Response, Flask   # Stream data to client
from flask_cors import CORS


def create_parser():
    """ Create the console arguments parser"""
    parser = argparse.ArgumentParser(description='Send random data to client',
                        usage='%(prog)s [options]', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--n_data', default=1, type=int,
                        help="amount of data to stream per chunk of samples")

    group_rand = parser.add_argument_group(title="Random", description=None)
    group_rand.add_argument('--rmin', default=0, type=float,
                        help="Min range for random")
    group_rand.add_argument('--rmax', default=100, type=float,
                        help="Max range for random")


    group_sconn = parser.add_argument_group(title="Stream connection", description=None)
    group_sconn.add_argument('--ip', default="localhost", type=str,
                        help="Host ip to do the streaming")
    group_sconn.add_argument('--port', default=8889, type=int,
                        help="Port to send the data to")
    group_sconn.add_argument('--url', default="/data/muse", type=str,
                        help="Path in the client to send the data, so it will be sent to 'http://ip:port/url'")


    return parser

def main():
    """ main function"""

    # REVIEW: fix imports


    # Parse args
    parser = create_parser()
    args = parser.parse_args()

    ##### Queues para stream datos, thread safe
    # Productor: random data
    # Consumidor: flask, que manda datos a client
    msize = 20 # maxsize
    q_data = deque(maxlen=msize)
    q_time = deque(maxlen=msize)
    lock_queues = threading.Lock()

    def generate_random_data(minrand, maxrand):
        """Generates random data"""

        absolute_t = 0
        print("Started generating random data")
        while True:
            # Crear tiempos
            timestamps = np.linspace(absolute_t, absolute_t+1, 12)
            absolute_t += 1


            # Random data in [0, 1]
            data = np.random.rand(5, 12)

            # Transform data in range
            data = data*(maxrand - minrand) + minrand

            # Agregar datos a queue
            with lock_queues:
                q_time.append(timestamps)
                q_data.append(data)

            sleep(0.08)





    # Generador para streaming
    app = Flask(__name__) # iniciar app de Flask
    CORS(app) # para que cliente pueda acceder a este puerto
    @app.route(args.url)
    def stream_data():
        """ """
        n_data = args.n_data
        def event_stream():
            # Drop old data
            t_init = 0

            with lock_queues:
                # Set an initial time as marker
                if len(q_time) > 0:
                    t_init = q_time[-1][0]
                q_time.clear()
                q_data.clear()


            # Stream
            while True:
                # sleep(0.1)
                lock_queues.acquire()
                if(len(q_time) == 0 or len(q_data) == 0): # NOTE: ambas length debiesen ser iguales siempre
                    # No data, continue
                    lock_queues.release()
                    continue

                # Tomar dato que viene
                t = q_time.popleft()
                d = q_data.popleft()
                lock_queues.release()

                # NOTE: if len(t) != 12 or d.shape != (5, 12) : may be an index exception
                for i in range(n_data):
                    tt = t[i] - t_init
                    yield "data: {}, {}, {}, {}, {}, {}\n\n".format(
                                tt, \
                                d[0][i], \
                                d[1][i], \
                                d[2][i], \
                                d[3][i], \
                                d[4][i] )

        return Response(event_stream(), mimetype="text/event-stream")

    # Thread para streaming
    stream = threading.Thread(target=app.run, kwargs={"host":args.ip, "port":args.port})
    stream.daemon = True

    gendata = threading.Thread(target=generate_random_data, args=(args.rmin, args.rmax))
    gendata.daemon = True

    ## Iniciar
    gendata.start()
    stream.start()

    while True:
        sleep(1)

    return 0


if __name__ == "__main__":
    main()
