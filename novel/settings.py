import redis

JSON_LD_DEFAULT_TYPE = 'Book'
redis_image = redis.StrictRedis(host='localhost', port=6379, db=1)
