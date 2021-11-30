import json
from random import randint
import random
import json
import datetime as dt
from config import Parser
from database.mongo_helper import MongoHelper
from database.classes import Item, Sensor, Event

mongo_helper = MongoHelper.init_from_config(Parser())

vet = [
    "6A003E74F2D2",
    "6A003E3D721B",
    "6A003E7E416B",
    "6A003E818B5E",
    "6A003E3D721B",
    "6A003E74F2D2"
]
lorem = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book."


for i in range(0xffff01, 0xffff05):
    Sensor(mongo_helper)._create_from_script({
        "sensor_id": hex(i)[2:],
        "name": f'sensor_{randint(0,20)}',
        "types": "RFID",
        "tag": "test",
        "description": lorem
    })

for i, tag_id in enumerate(vet):
    Item(mongo_helper)._create_from_script({
        "item_id": i,
        "name": "Notebook Dell FFAABBCC0%d" % i,
        "tags": [tag_id],
        "location_blacklist": "None",
        "location_whitelist": "All",
        "default_storage_location": "CC02",
        "description": lorem
    })

for i in range(0xffff01, 0xffff05):
    Event(mongo_helper)._create_from_script({
        "received_timestamp": dt.datetime.now(),
        "event_timestamp": dt.datetime.now(),
        "event_details": "tag in motion",
        "sensor_id": hex(i),
        "item_id": randint(0,5),
        "tag_id": random.choice(vet)
    })