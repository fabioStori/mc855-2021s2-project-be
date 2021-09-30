import pymongo.database
import pymongo

from datetime import datetime


class MongoHelper:

    @classmethod
    def init_from_config(cls, config):
        return MongoHelper(
            host=config.get("mongodb", "host"),
            port=int(config.get("mongodb", "port")),
            username=config.get("mongodb", "username"),
            password=config.get("mongodb", "password"),
            auth_source=config.get("mongodb", "auth_source"),
            database=config.get("mongodb", "database"),
        )

    def __init__(self, host, port, username, password, auth_source, database):

        self.db = pymongo.MongoClient(host=host,
                                      port=port,
                                      username=username,
                                      password=password,
                                      authSource=auth_source)[database]

    def get_event_count(self):
        return self.db["event"].find({}).count()

    def add_event(self, event):
        if not self.db["event"].find_one({"event_hash": event["event_hash"]}):
            event["inserted_timestamp"] = datetime.now()
            return self.db["event"].insert_one(event)

