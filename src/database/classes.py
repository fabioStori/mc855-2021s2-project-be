import uuid
from abc import abstractmethod
from datetime import datetime

import bson
from bson import ObjectId

from database.mongo_helper import MongoHelper, DuplicatedItemException


class MissingAttributeException(Exception):
    def __init__(self, attribute):
        self.attribute = attribute
        message = "Attribute %s is required, but not present in request" % attribute
        super().__init__(message)


DELETED_FIELD = "__deleted"


class DatabaseClassObj:
    @property
    @abstractmethod
    def collection_name(self):
        pass

    @property
    @abstractmethod
    def fields(self):
        pass

    @property
    @abstractmethod
    def required_fields(self):
        pass

    @property
    @abstractmethod
    def unique_fields(self):
        pass

    @property
    @abstractmethod
    def search_fields(self):
        pass

    @property
    @abstractmethod
    def id_field(self):
        pass

    default_fields = ["_id", DELETED_FIELD]

    def __fields__(self):
        return self.default_fields + self.fields

    def __init__(self, mongo_helper: MongoHelper, _id = None):
        self.mongo_helper = mongo_helper
        if _id is not None:

            ids_query = [{self.id_field: _id, DELETED_FIELD: {"$exists": False}}]
            try:
                ids_query.append({"_id": ObjectId(_id), DELETED_FIELD: {"$exists": False}})
            except bson.errors.InvalidId:
                pass

            obj = self.mongo_helper.db[self.collection_name].find_one({"$or": ids_query})
            if not obj:
                raise ValueError("Object with %s = %s in collection %s not found" % (self.id_field, _id,
                                                                                     self.collection_name))
            self._create_from_mongo_entry(obj)

    def __getitem__(self, item):
        if item in self.__fields__():
            return self.__getattribute__(item)
        else:
            raise AttributeError()

    def __setitem__(self, key, value):
        if key in self.__fields__():
            return self.__setattr__(key, value)
        else:
            raise AttributeError()

    def __contains__(self, item):
        return hasattr(self, item)

    def __iter__(self):
        for field in self.__fields__():
            if field in self:
                if field == "_id":
                    yield field, str(self[field])
                else:
                    yield field, self[field]

    def mongo_update_dict(self):
        return {"$set": {k: v for k, v in dict(self).items() if k != "_id"}}

    def create_from_request(self, request):
        for field in self.__fields__():
            if request.json.get(field) is not None:
                self[field] = request.json.get(field)

        for field in self.required_fields:
            if request.json.get(field) is None:
                raise MissingAttributeException(field)

        for field in self.unique_fields:
            if field in self:
                if self.mongo_helper.db[self.collection_name].find_one({field: self[field], DELETED_FIELD: {"$exists": False}}):
                    raise DuplicatedItemException(request)

        if "_id" in self and self["_id"]:
            raise TypeError("Unable to create item, _id attribute already set")

        inserted = self.mongo_helper.db[self.collection_name].insert_one(dict(self))
        self["_id"] = inserted.inserted_id
        return self

    def _create_from_mongo_entry(self, entry):
        for k, v in entry.items():
            self.__setattr__(k, v)
        return self

    def _create_from_script(self, entry):
        self.mongo_helper.db[self.collection_name].insert_one(dict(entry))
        return self

    def update_in_db(self):
        if "_id" not in self and self.id_field not in self:
            raise MissingAttributeException("_id")

        if "_id" in self:
            self.mongo_helper.db[self.collection_name].update_one({"_id": ObjectId(self["_id"])},
                                                                  self.mongo_update_dict())
        else:
            self.mongo_helper.db[self.collection_name].update_one({self.id_field, self[self.id_field]},
                                                                  self.mongo_update_dict())

    def update_from_request(self, request):
        if "_id" not in self and self.id_field not in self:
            raise MissingAttributeException("_id")

        for k, v in request.json.items():
            if k in self.__fields__():
                self.__setattr__(k, v)
        self.update_in_db()


    def delete(self):
        if "_id" not in self and self.id_field not in self:
            raise MissingAttributeException("_id")

        if "_id" in self:
            self.mongo_helper.db[self.collection_name].update_one({"_id": ObjectId(self["_id"])},
                                                                  {"$set": {DELETED_FIELD: True}})
        else:
            self.mongo_helper.db[self.collection_name].update_one({self.id_field, self[self.id_field]},
                                                                  {"$set": {DELETED_FIELD: True}})

    def search(self, query_regex, return_objects=False):
        resultset = self.mongo_helper.db[self.collection_name].find(
            {'$and': [
                {DELETED_FIELD: {"$exists": False}},
                {"$or": [
                    {field: {'$regex': query_regex, '$options': 'i'}}
                    for field in self.search_fields
                ]}
            ]}
           )
        objects = (self.__class__(self.mongo_helper)._create_from_mongo_entry(x) for x in resultset)
        if return_objects:
            return list(objects)
        return list(dict(o) for o in objects)

    def get_all(self):
        resultset = self.mongo_helper.db[self.collection_name].find(
            {DELETED_FIELD: {"$exists": False}}
        )
        objects = (self.__class__(self.mongo_helper)._create_from_mongo_entry(x) for x in resultset)
        return list(dict(o) for o in objects)

    def count(self):
        return self.mongo_helper.db[self.collection_name].find({DELETED_FIELD: {"$exists": False}}).count()


class Item(DatabaseClassObj):
    collection_name = "item"
    fields = ["description", "name", "tags",
              "default_storage_location", "location_blacklist",
              "location_whitelist", "item_id"]
    id_field = "item_id"
    unique_fields = ["item_id", "tags"]
    required_fields = ["name", "item_id", "tags"]
    search_fields = ["name", "item_id", "description", "tags"]


class Map(DatabaseClassObj):
    collection_name = "maps"
    fields = ["name", "image_link"]
    id_field = "name"
    unique_fields = ["image_link", "name"]
    required_fields = ["name", "image_link"]
    search_fields = ["name", "image_link"]


class Sensor(DatabaseClassObj):
    collection_name = "sensor"
    fields = ["description", "name", "sensor_id",
              "tag", "types"]
    id_field = "sensor_id"
    unique_fields = ["sensor_id"]
    required_fields = ["name", "sensor_id"]
    search_fields = ["name", "sensor_id", "description", "tag"]


USER_ACCESS_LIMITED = 2
USER_ACCESS_DEFAULT = 1
USER_ACCESS_MASTER = -1

ACCESS_DICT = {
    'limited': USER_ACCESS_LIMITED,
    'default': USER_ACCESS_DEFAULT,
    'master': USER_ACCESS_MASTER
}


class User(DatabaseClassObj):
    collection_name = "user"
    fields = ["email", "name", "creation_date",
              "access"]
    id_field = "email"
    unique_fields = ["email"]
    required_fields = ["name", "email", "access"]
    search_fields = ["email", "name", "creation_date",
                     "access"]

    acceptable_access = [USER_ACCESS_LIMITED, USER_ACCESS_DEFAULT, USER_ACCESS_MASTER]

    def __setitem__(self, key, value):
        if key == 'access':
            if value in ACCESS_DICT:
                value = ACCESS_DICT[value]
        super(User, self).__setitem__(key, value)

    def create_from_request(self, request):
        if request.json.get('access') not in self.acceptable_access and request.json.get('access') not in ACCESS_DICT:
            raise MissingAttributeException("attribute access is present, but invalid")
        return super(User, self).create_from_request(request)

    def update_from_request(self, request):
        if request.json.get('access'):
            if request.json['access'] not in self.acceptable_access:
                raise MissingAttributeException("attribute access is present, but invalid")
        return super(User, self).update_from_request(request)

    def create_from_raw_data(self, entry):
        self._create_from_mongo_entry(entry)
        inserted = self.mongo_helper.db[self.collection_name].insert_one(dict(self))
        self["_id"] = inserted.inserted_id
        return self


class Event(DatabaseClassObj):
    collection_name = "event"
    fields = ["received_timestamp", "event_timestamp", "event_details",
              "sensor_id", "item_id", "tag_id", "alert"]
    id_field = "event_timestamp"
    unique_fields = ["event_timestamp"]
    required_fields = ["received_timestamp", "event_timestamp", "event_details",
                       "sensor_id", "tag_id"]
    search_fields = ["event_details", "sensor_id", "item_id", "tag_id"]

    def filter_events(self, sensor_id=None, item_id=None, start_timestamp_range=None, end_timestamp_range=None, limit=None, skip=0):
        filters = []
        if sensor_id is not None:
            if isinstance(sensor_id, list):
                filters.append({'sensor_id': {"$in": sensor_id}})
            else:
                filters.append({'sensor_id': sensor_id})

        if item_id is not None:
            if isinstance(item_id, list):
                filters.append({'item_id': {"$in": item_id}})
            else:
                filters.append({'item_id': item_id})

        if start_timestamp_range is not None or end_timestamp_range is not None:
            filter_event = {}
            if start_timestamp_range:
                filter_event["$gte"] = start_timestamp_range

            if end_timestamp_range:
                filter_event["$lte"] = end_timestamp_range

            filters.append({'event_timestamp': filter_event})

        q = {}
        if filters:
            q['$and'] = filters

        q = self.mongo_helper.db[self.collection_name].find(q).sort([("event_timestamp", -1)])
        if skip:
            q.skip(skip)
        if limit:
            q.limit(limit)

        objects = (self.__class__(self.mongo_helper)._create_from_mongo_entry(x) for x in q)
        return list(dict(o) for o in objects)


class Token(DatabaseClassObj):
    collection_name = "token"
    fields = ["last_modified", "token", "user_data", "access_level"]
    id_field = "token"
    unique_fields = ["token"]
    required_fields = ["token", "user_data", "access_level"]
    search_fields = []

    def check_token_ttl(self):
        self.mongo_helper.db[self.collection_name].create_index(
           "last_modified", expireAfterSeconds=24*60*60, name="last_modified_ttl")

    def create_from_request(self, request):
        raise NotImplementedError()

    def create_token_from_user_data(self, user_data):
        self.check_token_ttl()
        self['last_modified'] = datetime.now()
        self['user_data'] = user_data
        self['access_level'] = user_data["access"]
        self['token'] = str(uuid.uuid4())

        inserted = self.mongo_helper.db[self.collection_name].insert_one(dict(self))
        self["_id"] = inserted.inserted_id
        return self['token']

    def update_token(self):
        self['last_modified'] = datetime.now()
        self.update_in_db()