from random import randint

from config import Parser
from database.mongo_helper import MongoHelper

mongo_helper = MongoHelper.init_from_config(Parser())

for i in range(0xffff01, 0xffff05):
    mongo_helper.add_sensor({
        "sensor_id": hex(i)[2:],
        "type": "RFID",
        "location": "Sala %d" % randint(0, 10)
    })

for i, tag_id in enumerate([
    "6A003E74F2D2",
    "6A003E3D721B",
    "6A003E7E416B",
    "6A003E818B5E",
    "6A003E3D721B",
    "6A003E74F2D2"
]):
    mongo_helper.add_item({
        "item_id": i,
        "name": "Notebook Dell FFAABBCC0%d" % i,
        "tags": [tag_id]
    })

