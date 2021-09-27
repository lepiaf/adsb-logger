import logging
import sys

import pyModeS as pms
from pyModeS.extra.rtlreader import RtlReader


class RtlSdrSource(RtlReader):
    def __init__(self):
        super(RtlSdrSource, self).__init__()

    def handle_messages(self, messages):
        if self.stop_flag.value is True:
            self.sdr.close()
            sys.exit(0)

        for msg, t in messages:
            if len(msg) < 28:  # only process long messages
                continue

            logging.debug("Raw message: {}".format(msg))
            df = pms.df(msg)

            if df == 17 or df == 18:
                logging.debug("Send message to pipe: {}".format(msg))
                self.raw_pipe_in.send(msg)
            else:
                continue
