import time
import traceback

import pyModeS as pms

from transformers import Transformers


class Decode:
    def __init__(self, transformers: Transformers, reference_position: dict) -> None:
        self.transformers = transformers
        self.reference_position = reference_position

    def process_raw(self, msg):
        icao = pms.icao(msg)
        tc = pms.adsb.typecode(msg)

        data = {
            "icao": icao,
            "tc": tc,
            "cs": pms.adsb.callsign(msg) if 1 <= tc <= 4 else None,
            "velocity": pms.adsb.velocity(msg) if (5 <= tc <= 8) or (tc == 19) else None,
            "alt": pms.adsb.altitude(msg) if (not (tc < 5 or tc == 19 or tc > 22)) else None,
            "position": pms.adsb.position_with_ref(msg, self.reference_position['latitude'],
                                                   self.reference_position['longitude']) if (5 <= tc <= 8) or (
                    9 <= tc <= 18 or 20 <= tc <= 22) else None,
        }

        return self.transformers.transform(data)

    def run(self, raw_pipe_out, ac_pipe_in, exception_queue):

        while True:
            try:
                while raw_pipe_out.poll():
                    data = raw_pipe_out.recv()
                    decoded = self.process_raw(data)
                    ac_pipe_in.send(decoded)

                time.sleep(0.001)

            except Exception as e:
                tb = traceback.format_exc()
                exception_queue.put((e, tb))
