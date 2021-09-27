import logging
import signal
import sys
import time
import traceback

import pyModeS as pms

from transformers import Transformers


class Decode:
    def __init__(self, transformers: Transformers, reference_position: dict) -> None:
        self.transformers = transformers
        self.reference_position = reference_position

    def stop(self, signal: int, frame):
        logging.debug('Stopping decode process')
        sys.exit(0)

    def process_raw(self, msg):
        icao = pms.icao(msg)
        tc = pms.adsb.typecode(msg)

        data = {
            "icao": icao,
            "type_code": tc,
            "call_sign": pms.adsb.callsign(msg) if 1 <= tc <= 4 else None,
            "velocity": pms.adsb.velocity(msg) if (5 <= tc <= 8) or (tc == 19) else None,
            "altitude": pms.adsb.altitude(msg) if (not (tc < 5 or tc == 19 or tc > 22)) else None,
            "position": pms.adsb.position_with_ref(msg, self.reference_position['latitude'],
                                                   self.reference_position['longitude']) if (5 <= tc <= 8) or (
                        9 <= tc <= 18 or 20 <= tc <= 22) else None,
        }

        return self.transformers.transform(data)

    def run(self, raw_pipe_out, ac_pipe_in):
        logging.debug('Start decode process')

        signal.signal(signal.SIGTERM, self.stop)

        while True:
            while raw_pipe_out.poll():
                data = raw_pipe_out.recv()
                decoded = self.process_raw(data)
                ac_pipe_in.send(decoded)

            time.sleep(0.001)
