from autoslug import AutoSlugField
from autoslug.utils import slugify
from django.db import models
from unidecode import unidecode

from django_cms import settings
from django_cms.utils.template_config import TEMPLATE_PAGE_CHOISES, TEMPLATE_INCLUDE_CHOISES
from django_cms.utils.helpers import code_validate


def unicode_slugify(name):
    return slugify(unidecode(name).replace(".", "-")).strip("-")


PAGE_TYPE = [
    ('text/plain', 'text/plain'),
    ('html', 'HTML'),
]


class HtmlPage(models.Model):
    class Meta:
        db_table = 'cms_pages'

    name = models.CharField(max_length=250, unique=True)
    slug = AutoSlugField(populate_from='name', slugify=unicode_slugify,
                         max_length=250, unique=True)
    content = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=30, blank=True, default='html', choices=PAGE_TYPE)
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return f"/{self.slug}"


class FooterInfo(models.Model):
    class Meta:
        db_table = "cms_footer"

    type = models.CharField(max_length=30, blank=True, default='copyright', unique=True)
    content = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)


class Link(models.Model):
    class Meta:
        db_table = "cms_link"

    name = models.CharField(max_length=250, unique=True)
    url = models.CharField(max_length=255, null=True)
    type = models.CharField(max_length=30, blank=True, default='hashtag')
    class_name = models.CharField(max_length=250, blank=True, null=True)
    active = models.BooleanField(default=True)


class Menu(models.Model):
    class Meta:
        db_table = "cms_menus"
        unique_together = [("name", "type")]
        ordering = ["type", "priority"]

    priority = models.SmallIntegerField(default=0)
    name = models.CharField(max_length=250)
    url = models.CharField(max_length=255)
    icon = models.CharField(max_length=250, blank=True, null=True)
    type = models.CharField(max_length=30, blank=True, null=True)
    extra_class = models.CharField(max_length=50, blank=True, null=True)
    require_logged = models.BooleanField(default=False)
    active = models.BooleanField(default=True)


def json_template_default():
    return {
        "default": {}
    }


class PageTemplate(models.Model):
    """
    all class handling for this model must be define in TEMPLATE_PAGE_CHOISES at CMS application.
    PATH: cms/template_config.py
    """

    class Meta:
        db_table = "cms_template_manager"
        ordering = ["page_file"]

    page_file = models.CharField(max_length=250, choices=TEMPLATE_PAGE_CHOISES.get(settings.APP_NAME),
                                 unique=True)
    params = models.JSONField(blank=True, null=True, default=json_template_default)

    @property
    def include_template(self):
        return InludeTemplate.objects.filter(template=self, active=True).order_by("priority").all()

    def __str__(self):
        return self.page_file.upper()


class InludeTemplate(models.Model):
    """
    all class handling for this model must be define in TEMPLATE_INCLUDE_CHOISES at CMS application.
    PATH: cms/template_config.py
    """

    class Meta:
        db_table = "cms_template_include"
        unique_together = [('template', 'code')]
        ordering = ["template", "priority"]

    priority = models.IntegerField(default=0)
    template = models.ForeignKey(PageTemplate, on_delete=models.CASCADE)
    code = models.CharField(max_length=50, validators=[code_validate])
    include_file = models.CharField(max_length=250, choices=TEMPLATE_INCLUDE_CHOISES.get(settings.APP_NAME))
    params = models.JSONField(blank=True, null=True, default=json_template_default)
    class_name = models.CharField(max_length=250, null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code


CAMPAIGN_STATUS = [
    ('running', 'RUNNING'),
    ('stopped', 'STOPPED'),
]


class CDNServer(models.Model):
    class Meta:
        db_table = "cdn_server"
        ordering = ["name"]

    # campaign_source = models.ForeignKey(CrawlCampaignSource, on_delete=models.CASCADE)
    name = models.CharField(max_length=250, unique=True)
    server_id = models.CharField(max_length=250, blank=True, null=True)
    endpoint = models.CharField(max_length=250)
    friendly_url = models.CharField(max_length=250, default='https://f000.backblazeb2.com/file/nettruyen/')
    friendly_alias_url = models.CharField(max_length=250, default='https://cdn.nettruyen.vn/file/nettruyen/')
    s3_url = models.CharField(max_length=250, blank=True, null=True)
    referer = models.CharField(max_length=250, blank=True, null=True)

    last_run = models.DateTimeField(default=None, null=True, blank=True)
    active = models.BooleanField(default=True)
    status = models.CharField(max_length=10, choices=CAMPAIGN_STATUS, default='stopped')

    def __str__(self):
        return self.name

    @classmethod
    def get_cdn(cls):
        return cls.objects.first()

    @classmethod
    def get_available_cdn(cls):
        return cls.objects.filter(active=True, status='stopped').all()

    @classmethod
    def get_active_cdn(cls):
        return cls.objects.filter(active=True).all()
