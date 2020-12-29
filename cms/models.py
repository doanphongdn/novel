from autoslug import AutoSlugField
from autoslug.utils import slugify
from django.db import models
from unidecode import unidecode


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
