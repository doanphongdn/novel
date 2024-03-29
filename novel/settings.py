import os

import redis

NEW_CHAPTER_NOTIFY_MSG = os.environ.get('NEW_CHAPTER_NOTIFY_MSG', 'New chapter %s, %s')
JSON_LD_DEFAULT_TYPE = 'Book'
redis_image = redis.StrictRedis(host='localhost', port=6379, db=1)
CHAPTER_CONFIG_ENABLE = os.environ.get('CHAPTER_CONFIG_ENABLE', 'false').lower() == 'true'

GOOGLE_RECAPTCHA_SITE_KEY = os.environ.get('GOOGLE_RECAPTCHA_SITE_KEY', '')
GOOGLE_RECAPTCHA_SECRET_KEY = os.environ.get('GOOGLE_RECAPTCHA_SECRET_KEY', '')
GOOGLE_ADS = os.environ.get('GOOGLE_ADS', '')
STREAM_IMAGE_DOMAIN = os.environ.get('STREAM_IMAGE_DOMAIN', '')
