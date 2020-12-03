from django.db import models

from django.core.exceptions import ValidationError
import re

from django.db.models import Q


def code_validate(value):
    reg = re.compile('^[a-zA-Z0-9_]+$')
    if not reg.match(value):
        raise ValidationError(u'<%s> must be character, number or underline' % value)


class CrawlCampaign(models.Model):
    class Meta:
        db_table = "crawl_campaigns"

    code = models.CharField(max_length=50, validators=[code_validate])
    name = models.CharField(max_length=250)
    source_url = models.CharField(max_length=250)
    pagination = models.BooleanField(default=False)
    page_format = models.CharField(max_length=50)

    @property
    def items(self):
        return CrawlItem.objects.filter(Q(parent_code=None) | Q(parent_code__isnull=True), campaign=self).all()


class CrawlItem(models.Model):
    class Meta:
        db_table = "crawl_campaign_items"

    campaign = models.ForeignKey(CrawlCampaign, on_delete=models.CASCADE)
    parent_code = models.CharField(max_length=50, null=True, blank=True)
    code = models.CharField(max_length=50, validators=[code_validate])
    name = models.CharField(max_length=250)
    xpath = models.CharField(max_length=250)
    xpath_property = models.CharField(max_length=50, null=True, blank=True,
                                      help_text="@src, @href, text, html ..., Blank if parent item.")

    @property
    def childrens(self):
        return CrawlItem.objects.filter(parent_code=self.code).all()
