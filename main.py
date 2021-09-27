import logging
import multiprocessing
import os
import signal
import sys
import time

from dotenv import load_dotenv

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
    recv_process.join(timeout=30)
    decode_process.join(timeout=30)
    record_process.join(timeout=30)


def close_all(signal: int, frame):
    logging.info("Signal {}. Cleaning up...".format(signal))
    shutdown()
    sys.exit(0)


if __name__ == '__main__':
    load_dotenv()
    logging.basicConfig(level=os.getenv('LOG_LEVEL'))
    logging.info('Start main process')

    raw_pipe_in, raw_pipe_out = multiprocessing.Pipe()
    ac_pipe_in, ac_pipe_out = multiprocessing.Pipe()
    exception_queue = multiprocessing.Queue()
    stop_flag = multiprocessing.Value("b", False)

    transformers = Transformers()
    transformers.transformers.append(Position())
    transformers.transformers.append(Velocity())

    source = RtlSdrSource()
    recv_process = multiprocessing.Process(target=source.run, args=(raw_pipe_in, stop_flag, exception_queue))

    decode = Decode(
        transformers,
        {'latitude': os.getenv('REFERENCE_LATITUDE'), 'longitude': os.getenv('REFERENCE_LONGITUDE')}
    )
    decode_process = multiprocessing.Process(target=decode.run, args=(raw_pipe_out, ac_pipe_in))

    record = Record(mongodb_uri=os.getenv('MONGODB_URI'))
    record_process = multiprocessing.Process(target=record.run, args=(ac_pipe_out,))

    signal.signal(signal.SIGINT, close_all)
    signal.signal(signal.SIGTERM, close_all)

    recv_process.start()
    decode_process.start()
    record_process.start()

    while True:
        if (not recv_process.is_alive()) or (not record_process.is_alive()) or (not decode_process.is_alive()):
            shutdown()
            sys.exit(1)

        time.sleep(0.01)
