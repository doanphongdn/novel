import redis


class RedisNovelContent(object):
    redisdb = redis.StrictRedis(host='localhost', port=6379, db=1)

    @classmethod
    def set(cls, key, value):
        cls.redisdb.set(key, value)

    @classmethod
    def get(cls, key):
        return cls.redisdb.get(key)
