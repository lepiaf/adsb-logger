import time
import traceback
from datetime import datetime, timezone

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


class Record:
    def __init__(self):
        self.stop_flag = False
        self.client = None
        self.db = None
        self.collection = None

    def stop(self):
        self.client.close()
        return

    def record_entry(self, data):
        now = datetime.now(timezone.utc)
        data['created_at'] = now

        print(data)
        self.collection.insert_one(data)

    def run(self, ac_pipe_out, stop_flag=None, exception_queue=None):
        self.stop_flag = stop_flag

        if self.stop_flag.value is True:
            self.stop()
            return

        self.client = MongoClient("mongodb://adsb:adsb@127.0.0.1:27017")
        self.db: Database = self.client['adsb']
        self.collection: Collection = self.db['message']

        while True:
            try:
                while ac_pipe_out.poll():
                    data = ac_pipe_out.recv()
                    self.record_entry(data)

                time.sleep(0.001)

            except Exception as e:
                tb = traceback.format_exc()
                exception_queue.put((e, tb))
