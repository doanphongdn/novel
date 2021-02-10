import redis

JSON_LD_DEFAULT_TYPE = 'Book'
redis_image = redis.StrictRedis(host='localhost', port=6379, db=1)

GOOGLE_RECAPTCHA_SITE_KEY = '6LcjxlEaAAAAAG_5o_Eoq4jOt6i54pu-K2Zu7IcU'
GOOGLE_RECAPTCHA_SECRET_KEY = '6LcjxlEaAAAAAD9RzVrMcfASf-VGhLf5wJQDcYgR'
