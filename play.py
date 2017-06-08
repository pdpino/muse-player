#!/usr/bin/env python
"""Play muse data

Connects with a muse (2016) device, stream the data through a text/event-stream and save the data to a csv"""

from time import sleep, time
from collections import deque
import numpy as np
import pandas as pd
import argparse
import threading
from flask import Response, Flask   # Stream data to client
from flask_cors import CORS
from muse import Muse
import data_mng
import basic



# Next TODOs:
# TODO: Interrumpir todos threads con un solo ctrl+c # use signal handler?
# TODO: despues de un rato vaciar listas full_data y full_time, se llenan mucho # opcion para guardarlas como dump o no
# TODO: dejar opcion para stream promedio o todos los datos
# IDEA: probar qué tanta información se pierde en mandar promedio, un dato o todos
    # calcular cov o dispersion de 12 samples (?)

# Not urgent
# TODO: ordenar README_develop seccion "headband en estado normal"
# IDEA: expandir muse module para que chequee estado bateria y reciba aceletrometro, etc

def normalize_time(timestamps):
    """Receive a list of np arrays of timestamps. Return the concatenated and normalized (substract initial time) np array"""

    # Concat y normalizar timestamps
    timestamps = np.concatenate(timestamps)
    return timestamps - timestamps[0]

def normalize_data(data):
    """Return the data concatenated"""
    return np.concatenate(data, 1).T

def save_csv(data, timestamps, fname, subfolder=None):
    """Preprocess the data and save it to a csv """
    # Concatenar data
    data = normalize_data(data)

    # Juntar en dataframe
    res = pd.DataFrame(data=data, columns=['TP9', 'AF7', 'AF8', 'TP10', 'Right AUX'])
    res['timestamps'] = timestamps

    # Guardar a csv
    data_mng.save_data(res, fname, subfolder)

def create_parser():
    """ Create the console arguments parser"""
    parser = argparse.ArgumentParser(description='Send muse data to client and save to .csv', usage='%(prog)s [options]')

    group_conn = parser.add_argument_group(title="Bluetooth connection", description=None)
    group_conn.add_argument('-i', '--interface', default=None, type=str,
                        help="Bluetooth interface")
    group_conn.add_argument('-a', '--address', default="00:55:DA:B3:20:D7", type=str,
                        help="Device's MAC address")

    group_data = parser.add_argument_group(title="Data arguments")
    group_data.add_argument('-t', '--time', default=None, type=float,
                        help="Seconds to record data (aprox). If none, stop listening only when interrupted")
    group_data.add_argument('-s', '--save', action="store_true",
                        help="Whether to save a .csv file with the data or not")
    group_data.add_argument('-f', '--fname', default="dump", type=str,
                        help="Name to store the .csv file. Only useful with -s")
    group_data.add_argument('-s', '--subfolder', default=None, type=str,
                        help="Subfolder to save the .csv file. Only useful with -s")

    group_stream = parser.add_argument_group(title="Stream connection")
    group_stream.add_argument('--ip', default="localhost", type=str,
                        help="Host ip to do the stream. Defaults to 'localhost'")
    group_stream.add_argument('--port', default=8889, type=int,
                        help="Port to send the data to. Defaults to 8889")
    group_stream.add_argument('--url', default="/data/muse", type=str,
                        help="sub-url to send the data. It will be sent to 'http://ip:port/url'. Defaults to /data/muse")

    return parser

def main():
    """Connect with muse and stream the data"""
    # Parse args
    parser = create_parser()
    args = parser.parse_args()


    # Preprocesar argumentos
    args.url = basic.assure_startswith(args.url, "/")

    ##### Queues para stream datos, thread safe
    # Productor: muse
    # Consumidor: flask, que manda datos a client
    msize = 10 # maxsize
    q_data = deque(maxlen=msize)
    q_time = deque(maxlen=msize)
    lock_queues = threading.Lock()

    ##### Listas para guardar datos
    full_time = []
    full_data = []

    def process_muse_data(data, timestamps):
        """Stores and enqueues the incoming muse data"""

        # data viene en ndarrays de 5x12 # 5 canales x 12 muestras
        # timestamps viene en ndarrays de 12x1 # 12 muestras
        full_time.append(timestamps)
        full_data.append(data)

        # Agregar datos a queue
        lock_queues.acquire()
        q_time.append(timestamps)
        q_data.append(data)
        lock_queues.release()


    ##### Stream datos
    app = Flask(__name__) # iniciar app de Flask
    CORS(app) # para que cliente pueda acceder a este puerto
    @app.route(args.url)
    def stream_data():
        def event_stream():
            # DEBUG:
            t_act = 0
            t_old = 0
            dt = 1 # print cada 1 seg

            # Drop old data
            lock_queues.acquire()
            q_time.clear()
            q_data.clear()
            t_init = time() # Set an initial time as marker
            lock_queues.release()

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
                for i in range(1): # NOTE: cambiar por 12 para stream all data
                    tt = t[i] - t_init
                    yield "data: {}, {}, {}, {}, {}, {}\n\n".format(tt, \
                                    d[0][i], \
                                    d[1][i], \
                                    d[2][i], \
                                    d[3][i], \
                                    d[4][i])
                    ### REVIEW: pasar datos mas eficientemente
                    # DEBUG:
                    # t_act = tt
                    #if(t_act - t_old >= dt): # 1 second passed
                        # print(t_act)
                        #t_old = t_act

                ## Calcular promedio de puntos -> stream promedio
                # tt = t.mean() - t_init
                # yield "data: {}, {}, {}, {}, {}, {}\n\n".format(tt, d[0].mean(), d[1].mean(), d[2].mean(), d[3].mean(), d[4].mean())

                # DEBUG: # print en que segundo va
                # t_act = tt
                # if(t_act - t_old >= dt): # 1 second passed
                #     print(t_act)
                #     t_old = t_act

        return Response(event_stream(), mimetype="text/event-stream")


    ##### Start muse
    muse = Muse(args.address, process_muse_data, interface=args.interface)
    status = muse.connect()
    if status != 0:
        basic.perror("Can't connect to muse band", exit_code=status)


    # Thread para streaming
    stream = threading.Thread(target=app.run, kwargs={"host":args.ip, "port":args.port})
    stream.daemon = True 

    ##### Init
    muse.start()
    stream.start()

    print("Started receiving muse data...")
    if args.time is None:
        print("\tpress ctrl+c to stop it")
        while 1:
            try:
                sleep(1)
            except:
                print("Interrupted")
                break
    else:
        print("\t for (aprox) {} seconds".format(args.time)) # HACK
        sleep(args.time)

    muse.stop()
    muse.disconnect()
    print("Stopped receiving muse data")


    ##### Guardar todo
    full_time = normalize_time(full_time)

    print("Received data for {:.2f} seconds".format(full_time[-1]))

    if args.save:
        save_csv(full_data, full_time, args.fname, folder=args.subfolder)



    # Matar todos threads
    return 0


if __name__ == "__main__":
    main()
