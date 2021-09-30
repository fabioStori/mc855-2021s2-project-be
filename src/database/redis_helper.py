import json
import redis

from abc import abstractmethod


class RedisHelper:
    def __init__(self, host='', port=11158):
        if not hasattr(self, '_pool'):
            self._pool = redis.ConnectionPool(host=host, port=port, db=0, password='')

    def set(self, val, key, subkey=None, expiration_time=None):
        if val is None:
            return
        r = redis.Redis(connection_pool=self._pool)
        if subkey:
            key = "%s_%s" % (key, subkey)

        if expiration_time:
            r.setex(name=key, value=val, time=expiration_time)
        else:
            r.set(name=key, value=val)

    def get(self, key, subkey=None, new_expiration_time=None):
        r = redis.Redis(connection_pool=self._pool, decode_responses=True)

        if subkey:
            key = "%s_%s" % (key, subkey)
        val = r.get(key)
        if new_expiration_time:
            r.expire(key, new_expiration_time)
        return val

    def set_dict(self, val, key, subkey=None, expiration_time=None):
        if not bool(val):
            return
        r = redis.Redis(connection_pool=self._pool)
        if subkey:
            key = "%s_%s" % (key, subkey)
        r.set(key, json.dumps(val))
        if expiration_time:
            r.expire(key, expiration_time)

    def get_dict(self, key, subkey=None, new_expiration_time=None):
        r = redis.Redis(connection_pool=self._pool)

        if subkey:
            key = "%s_%s" % (key, subkey)
        val = r.get(key)
        if new_expiration_time:
            r.expire(key, new_expiration_time)

        return json.loads(val) if val else None

    def flush_all(self):
        r = redis.Redis(connection_pool=self._pool)
        r.flushall()


class RedisObject:
    @abstractmethod
    def to_dict(self):
        pass

    @abstractmethod
    def from_dict(self, d):
        pass

    @classmethod
    @abstractmethod
    def load(cls, helper: RedisHelper, object_id):
        pass

    @abstractmethod
    def save(self, helper: RedisHelper):
        pass

    @property
    @abstractmethod
    def id(self):
        pass


class RedisError(Exception):
    pass

