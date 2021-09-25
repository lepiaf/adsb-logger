import multiprocessing
import signal
import sys
import time

from decode import Decode
from record import Record
from source import RtlSdrSource
from transformer.position import Position
from transformer.velocity import Velocity
from transformers import Transformers


def shutdown():
    stop_flag.value = True
    sys.stdout = sys.__stdout__
    recv_process.terminate()
    decode_process.terminate()
    record_process.terminate()
    recv_process.join()
    decode_process.join()
    record_process.join()


def closeall(signal: int, frame):
    print("KeyboardInterrupt (ID: {}). Cleaning up...".format(signal))
    shutdown()
    sys.exit(0)


if __name__ == '__main__':

    raw_pipe_in, raw_pipe_out = multiprocessing.Pipe()
    ac_pipe_in, ac_pipe_out = multiprocessing.Pipe()
    exception_queue = multiprocessing.Queue()
    stop_flag = multiprocessing.Value("b", False)

    transformers = Transformers()
    transformers.transformers.append(Position())
    transformers.transformers.append(Velocity())

    source = RtlSdrSource()
    recv_process = multiprocessing.Process(
        target=source.run, args=(raw_pipe_in, stop_flag, exception_queue)
    )

    decode = Decode(transformers, {'latitude': 0.0, 'longitude': 0.0})
    decode_process = multiprocessing.Process(
        target=decode.run, args=(raw_pipe_out, ac_pipe_in, exception_queue)
    )

    record = Record()
    record_process = multiprocessing.Process(
        target=record.run, args=(ac_pipe_out, stop_flag, exception_queue)
    )

    signal.signal(signal.SIGINT, closeall)

    recv_process.start()
    decode_process.start()
    record_process.start()

    while True:
        if (not recv_process.is_alive()) or (not decode_process.is_alive()):
            shutdown()
            while not exception_queue.empty():
                trackback = exception_queue.get()
                print(trackback)

            sys.exit(1)

        time.sleep(0.01)
