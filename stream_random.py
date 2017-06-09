#!/usr/bin/env python
"""Stream random data to client, used for debugging"""

from time import sleep, time
from collections import deque
import numpy as np
import argparse
import threading
import signal
from flask import Response, Flask   # Stream data to client
from flask_cors import CORS
import basic


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
    # Parse args
    parser = create_parser()
    args = parser.parse_args()

    # Argumentos
    args.url = basic.assure_startswith(args.url, "/")

    ##### Queues para stream datos, thread safe
    # Productor: random data
    # Consumidor: flask, que manda datos a client
    msize = 10 # maxsize
    q_data = deque(maxlen=msize)
    q_time = deque(maxlen=msize)
    lock_queues = threading.Lock()

    ##### Listas para guardar datos
    full_time = []
    full_data = []

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

            # Agregar a full lists
            full_time.append(timestamps)
            full_data.append(data)

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

        def get_data_n(tt, t_init, data, n):
            """Yield n out of the 12  """

        n_data = args.n_data

        def event_stream():
            # Drop old data
            with lock_queues:
                q_time.clear()
                q_data.clear()
                t_init = time() # Set an initial time as marker

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

    # Capturar ctrl-c
    catcher = basic.SignalCatcher()
    signal.signal(signal.SIGINT, catcher.signal_handler)

    ## Iniciar
    gendata.start()
    stream.start()

    while catcher.keep_running():
        sleep(1)

    return 0


if __name__ == "__main__":
    main()