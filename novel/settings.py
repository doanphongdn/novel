import os

import redis


NEW_CHAPTER_NOTIFY_MSG = os.environ.get('NEW_CHAPTER_NOTIFY_MSG', 'New chapter %s, %s')
JSON_LD_DEFAULT_TYPE = 'Book'
redis_image = redis.StrictRedis(host='localhost', port=6379, db=1)

GOOGLE_RECAPTCHA_SITE_KEY = os.environ.get('GOOGLE_RECAPTCHA_SITE_KEY', '')
GOOGLE_RECAPTCHA_SECRET_KEY = os.environ.get('GOOGLE_RECAPTCHA_SECRET_KEY', '')
GOOGLE_ADS = os.environ.get('GOOGLE_ADS', '')
