import os

import redis


JSON_LD_DEFAULT_TYPE = 'Book'
redis_image = redis.StrictRedis(host='localhost', port=6379, db=1)

GOOGLE_RECAPTCHA_SITE_KEY = os.environ.get('GOOGLE_RECAPTCHA_SITE_KEY', '')
GOOGLE_RECAPTCHA_SECRET_KEY = os.environ.get('GOOGLE_RECAPTCHA_SECRET_KEY', '')
GOOGLE_ADS = os.environ.get('GOOGLE_ADS', '')
GOOGLE_GPT_ADM_CODE = os.environ.get('GOOGLE_GPT_ADM_CODE', 'True').lower() == 'true'
