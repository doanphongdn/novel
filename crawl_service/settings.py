"""
Django settings for crawl_service project.

Generated by 'django-admin startproject' using Django 3.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
from pathlib import Path

from django.templatetags.static import static
# Build paths inside the project like this: BASE_DIR / 'subdir'.
from dotenv import load_dotenv

from custom_allauth.settings import *
from novel.settings import *
from .pipeline_config import *

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'), override=True, verbose=True)
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^6ezxsck574p4nub835ln78*x-gig1pjg-+$(o_82fo(h+#cu!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'

ALLOWED_HOSTS = ['*']

APP_NAME = os.environ.get('APP_NAME', 'novel')
NOVEL_ALL_URL = os.environ.get('NOVEL_ALL_URL', 'all')
NOVEL_GENRE_URL = os.environ.get('NOVEL_GENRE_URL', 'genre')
NOVEL_PAGE_URL = os.environ.get('NOVEL_PAGE_URL', 'page')
SELENIUM_LAZY_LOADING_TIMEOUT = int(os.environ.get('SELENIUM_LAZY_LOADING_TIMEOUT', 3))
SELENIUM_CHROME_DRIVE = os.environ.get('SELENIUM_CHROME_DRIVE', '/usr/local/bin/chromedriver')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django.contrib.postgres',
    'django_extensions',
    # allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'custom_allauth.socialaccount.providers.zalo',
    # other app
    'django_redis',
    'pipeline',
    'cms',
    'crawl_service',
    'rest_framework',
    'ckeditor',
    'django_json_widget',
    'structured_data',
    'django_backblaze_b2',
    APP_NAME,
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'pipeline.middleware.MinifyHTMLMiddleware',
]

ROOT_URLCONF = 'crawl_service.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

TEMPLATE_CONTEXT_PROCESSORS = (
    'django_admin_dialog.context_processors.django_admin_dialog',
)

WSGI_APPLICATION = 'crawl_service.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql_psycopg2'),
        'NAME': os.environ.get('DB_NAME', ''),
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASS', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s |  %(asctime)s | %(filename)s:%(lineno)d | %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': os.environ.get('LOGGING_LEVEL', 'INFO'),
            'class': 'logging.FileHandler',
            'filename': os.environ.get('LOGGING_FILE', '/var/log/crawl_service/daily.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': os.environ.get('LOGGING_LEVEL', 'INFO'),
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': os.environ.get('LOGGING_LEVEL', 'INFO'),
            'propagate': True,
        },
    },
}

CACHES = {
    'default': {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": "example"
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Ho_Chi_Minh'

USE_I18N = True

USE_L10N = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

SITE_ID = 1

STATIC_URL = '/static/'
STATIC_ROOT = os.environ.get('STATIC_ROOT')
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static_files"), os.path.join(BASE_DIR, "static_debug")]

MEDIA_ROOT = os.environ.get('MEDIA_ROOT')
MEDIA_URL = '/media/'

# Pipeline config


PIPELINE_STORAGE = 'pipeline.storage.PipelineCachedStorage'
STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
)
PIPELINE = {
    'PIPELINE_ENABLED': True,
    'COMPILERS': ('pipeline.compilers.sass.SASSCompiler',),
    'CSS_COMPRESSOR': 'pipeline.compressors.yuglify.YuglifyCompressor',
    'JS_COMPRESSOR': 'pipeline.compressors.yuglify.YuglifyCompressor',
    'SASS_BINARY': '/usr/local/bin/sass',
    'YUGLIFY_BINARY': '/usr/local/bin/yuglify',

    'STYLESHEETS': PIPELINE_STYLESHEETS.get(APP_NAME)
}

LOG_ENABLED = os.environ.get('LOG_ENABLED', 'false').lower() == 'true'
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARNING')
LOG_FILE = os.environ.get('LOG_FILE')

REDIS_HOST = '127.0.0.1'
REDIS_PORT = '6379'

CDN_FILE_FOLDER = os.environ.get('CDN_FILE_FOLDER', '/data/cdn/novel')

NOVEL_STATIC_IMAGE_FOLDER = "images/novel"
NOVEL_STATIC_IMAGE_PATH = os.path.join(STATIC_ROOT, NOVEL_STATIC_IMAGE_FOLDER)

if not os.path.exists(NOVEL_STATIC_IMAGE_PATH):
    os.makedirs(NOVEL_STATIC_IMAGE_PATH)

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': [
            ['Styles', 'Format', 'Font', 'FontSize'],
            ['Bold', 'Italic', 'Underline', 'StrikeThrough', '-', 'Undo', 'Redo', '-', 'Cut', 'Copy', 'Paste',
             'Find',
             'Replace', '-', 'Outdent', 'Indent', '-', 'Print'],
            ['NumberedList', 'BulletedList', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
        ],
        'height': 500,
        'width': 1000,
    },
}

CRAWL_TYPE_MAPPING = {
    APP_NAME: [
        ('NovelCampaignType', 'NOVEL'),
        ('NovelInfoCampaignType', 'NOVEL_INFO'),
        ('NovelChapterCampaignType', 'NOVEL_CHAPTER'),
    ]
}

CRAWL_ACTION_MAPPING = {
    APP_NAME: [
        ('ReverseAction', 'Reverse Chapter List'),
        ('FormatChapterContent', "Format Chapter Content"),
        ('GroupItem', "Group Items"),
        ('JoinItem', "Join Items"),
    ]
}

BACKBLAZE_CONFIG = {
    "application_key_id": os.environ.get('BACKBLAZE_KEY_ID', ""),  # however you want to securely retrieve these values
    "application_key": os.environ.get("BACKBLAZE_KEY", ""),
}

BACKBLAZE_MAX_RETRY = int(os.environ.get('BACKBLAZE_MAX_RETRY', 5))
BACKBLAZE_NOT_ALLOW_LIMIT = os.environ.get('BACKBLAZE_ALLOW_LIMIT', 'TRUE').lower() != 'true'
