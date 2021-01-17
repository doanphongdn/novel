import os
from os import listdir
from os.path import isfile

from autoslug import AutoSlugField
from autoslug.utils import slugify
from django.db import models
from unidecode import unidecode

from cms.template_config import TEMPLATE_PAGE_CHOISES, TEMPLATE_INCLUDE_CHOISES
from crawl_service import settings
from crawl_service.models import code_validate


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


class TemplateManager(models.Model):
    class Meta:
        db_table = "cms_template_manager"

    page_file = models.CharField(max_length=250, choices=TEMPLATE_PAGE_CHOISES.get(settings.APP_NAME),
                                 unique=True)
    includes_default = models.TextField()

    def include_template(self):
        return InludeTemplate.objects.filter(template=self, active=True).all()


class InludeTemplate(models.Model):
    class Meta:
        db_table = "cms_template_include"
        unique_together = [('template', 'code')]

    template = models.ForeignKey(TemplateManager, on_delete=models.CASCADE)
    code = models.CharField(max_length=50, validators=[code_validate])
    include_file = models.CharField(max_length=250, choices=TEMPLATE_INCLUDE_CHOISES.get(settings.APP_NAME))
    params = models.TextField()
    class_name = models.CharField(max_length=250)
    full_width = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
