import redis

from crawl_service import settings


class RedisStore(object):
    # Connect to our Redis instance
    redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                       port=settings.REDIS_PORT, db=0)
