import os
from os import listdir
from os.path import isfile

from autoslug import AutoSlugField
from autoslug.utils import slugify
from django.db import models
from unidecode import unidecode

from crawl_service import settings


def unicode_slugify(name):
    return slugify(unidecode(name).replace(".", "-")).strip("-")


class HtmlPage(models.Model):
    class Meta:
        db_table = 'cms_pages'

    name = models.CharField(max_length=250, unique=True)
    slug = AutoSlugField(populate_from='name', slugify=unicode_slugify,
                         max_length=250, unique=True)
    content = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return f"/{self.slug}"


class FooterInfo(models.Model):
    class Meta:
        db_table = "cms_footer"

    content = models.TextField(blank=True, null=True)
    copyright = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)


class Link(models.Model):
    class Meta:
        db_table = "cms_link"

    name = models.CharField(max_length=250, unique=True)
    url = models.CharField(max_length=255, null=True)
    type = models.CharField(max_length=30, blank=True, default='hashtag')
    active = models.BooleanField(default=True)


PAGE_FILES = [(f, f) for f in listdir(os.path.join(settings.BASE_DIR, "templates", os.environ.get('APP_NAME')))
              if isfile(os.path.join(settings.BASE_DIR, "templates", os.environ.get('APP_NAME'), f))
              and f.endswith(".html") and f != 'base.html']
INCLUDE_FILES = [(f, f) for f in
                 listdir(os.path.join(settings.BASE_DIR, os.environ.get('APP_NAME'), "views/includes" ))
                 if isfile(os.path.join(settings.BASE_DIR, "templates", os.environ.get('APP_NAME'), f))
                 and f.endswith(".html") and f != 'base.html']


class TemplateManager(models.Model):
    class Meta:
        db_table = "cms_template_manager"

    page_name = models.CharField(max_length=250, choices=PAGE_FILES)
    include_file = models.CharField(max_length=250, choices=INCLUDE_FILES)
