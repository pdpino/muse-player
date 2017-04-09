from muse import Muse
from time import sleep, time
import sys
import os
import numpy as np
import pandas as pd
import argparse
import threading
from collections import deque

from flask import Response, Flask   # Stream datos a client
from flask_cors import CORS

# OTRAS FUNCIONES
def perror(text, exit_code=1, **kwargs):
    print("ERROR: {}".format(text), file=sys.stderr, **kwargs)
    if exit_code > 0:
        sys.exit(exit_code)


# TODO: Signal handler para cortar todo en ctrl+c


if __name__ == "__main__":
    ##### Parsear argumentos
    parser = argparse.ArgumentParser(description='Record muse data to .csv', usage='%(prog)s [options]')
    parser.add_argument('-a', '--address', default="00:55:DA:B3:20:D7", type=str,
                        help="Device's mac address")
    parser.add_argument('-s', '--save_csv', action="store_true",
                        help="Whether to save a .csv file with the data or not")
    parser.add_argument('-f', '--filename', default="dump", type=str,
                        help="Name to store the .csv file. Only works with -s")
    parser.add_argument('-d', '--dir', default="data", type=str,
                        help="Subfolder to save the dump file")
    parser.add_argument('-t', '--time', default=None, type=float,
                        help="Seconds to record data (aprox)")

    args = parser.parse_args()


    ##### Queue, es thread safe
    # Productor: muse
    # Consumidor: flask, que manda datos a client
    msize = 10
    q_data = deque(maxlen=msize)
    q_time = deque(maxlen=msize)

    lock_queues = threading.Lock() #lock para agregar datos a ambas colas al mismo tiempo

    ##### Listas para guardar datos
    full_time = []
    full_data = []

    def process_muse_data(data, timestamps):
        # data viene en ndarrays de 5x12
            # 5 canales x 12 muestras
        # timestamps viene en ndarrays de 12x1
            # 12 muestras
        full_time.append(timestamps)
        full_data.append(data)

        # Agregar datos a queue
        lock_queues.acquire()
        q_time.append(timestamps)
        q_data.append(data)
        lock_queues.release()


    ##### Stream datos
    app = Flask(__name__)
    CORS(app)


    @app.route('/data/prueba')
    def stream_data():
        def event_stream():
            t_init = time()
            while True:
                lock_queues.acquire()
                if(len(q_time) == 0 or len(q_data) == 0): #ambas len debiesen ser iguales
                    # Si no hay datos, continue
                    lock_queues.release()
                    continue

                t = q_time.popleft()
                d = q_data.popleft()
                lock_queues.release()

                # NOTE: Si por alguna razon len(t) != 12 or d.shape != (5, 12) va a haber un error
                for i in range(12):
                    tt = t[i] - t_init
                    for ch in range(5):
                        yield "data: {}, {}, {}\n\n".format(ch, tt, d[ch][i])

        return Response(event_stream(), mimetype="text/event-stream")


    ##### Muse headband
    muse = Muse(args.address, process_muse_data)
    status = muse.connect()
    if status != 0:
        perror("Can't connect to muse band", exit_code=status)




    ##### Init
    stream = threading.Thread(target=app.run, kwargs={"host":"localhost", "port":8889})
    muse.start()
    stream.start() # app.run(host='localhost', port=8889)

    print("Started receiving...")
    if args.time is None:
        print("\t(press ctrl+c to stop it)")
        while 1:
            try:
                sleep(1)
            except:
                print("Interrupted")
                break
    else:
        print("\t for (aprox) {} seconds".format(args.time))
        sleep(args.time)

    muse.stop()
    muse.disconnect()
    print("Stopped receiving")


    ##### Guardar todo
    # Normalizar timestamps
    full_time = np.concatenate(full_time)
    full_time = full_time - full_time[0]

    print("Received data for {:.2f} seconds".format(full_time[-1]))

    if args.save_csv:
        # Filename para guardar csv
        filename = ""
        if args.dir != "":
            # concat filename
            filename = args.dir + "/"
            # Checkear que existe carpeta, sino crearla
            if not os.path.exists(args.dir):
                os.makedirs(args.dir, mode=0o775)

        filename += args.filename
        filename += ".csv"

        # Data
        full_data = np.concatenate(full_data, 1).T

        # Pasar a dataframe
        res = pd.DataFrame(data=full_data, columns=['TP9', 'AF7', 'AF8', 'TP10', 'Right AUX'])
        res['timestamps'] = full_time

        # Guardar a csv
        print("Saving to file {}".format(filename))
        res.to_csv(filename, float_format='%.3f')

    # Matar todos threads
    sys.exit(0)
