import logging
import signal
import sys
import time
import traceback
from datetime import datetime, timezone

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


class Record:
    def __init__(self, mongodb_uri: str):
        self.stop_flag = False
        self.client = None
        self.db = None
        self.collection = None
        self.mongodb_uri = mongodb_uri

    def stop(self, signal: int, frame):
        logging.debug("Stopping record process")
        self.client.close()
        sys.exit(0)

    def record_entry(self, data):
        data['timestamp'] = datetime.now(timezone.utc)

        logging.debug(msg="Record message to database: {}".format(data))
        self.collection.insert_one(data)

    def run(self, ac_pipe_out):
        logging.debug('Start record process')

        signal.signal(signal.SIGTERM, self.stop)

        self.client = MongoClient(self.mongodb_uri)
        self.db: Database = self.client['adsb']
        self.collection: Collection = self.db['message']

        while True:
            while ac_pipe_out.poll():
                data = ac_pipe_out.recv()
                self.record_entry(data)

            time.sleep(0.001)
