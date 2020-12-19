import re

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from crawl_service.services.campaign_type import CrawlCampaignType


def code_validate(value):
    reg = re.compile(r'^[a-zA-Z0-9_]+$')
    if not reg.match(value):
        raise ValidationError(u'<%s> must be character, number or underline' % value)


class CrawlCampaignSource(models.Model):
    class Meta:
        db_table = "crawl_campaign_sources"

    name = models.CharField(max_length=250)
    homepage = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class CrawlCampaign(models.Model):
    class Meta:
        db_table = "crawl_campaigns"

    campaign_source = models.ForeignKey(CrawlCampaignSource, on_delete=models.CASCADE)
    campaign_type = models.CharField(max_length=50, choices=CrawlCampaignType.list_types)
    name = models.CharField(max_length=250)
    target_url = models.CharField(max_length=250)
    page_param_name = models.CharField(max_length=50, null=True, blank=True, default='',
                                       help_text="Blank if no pagination.")
    active = models.BooleanField(default=True)

    def child_items(self):
        return CrawlItem.objects.filter(parent_code__isnull=False, campaign=self).exclude(parent_code=None).all()

    @property
    def parent_items(self):
        return CrawlItem.objects.filter(Q(parent_code=None) | Q(parent_code__isnull=True), campaign=self).all()

    def full_clean(self, exclude=None, validate_unique=True):
        pass


class CrawlItem(models.Model):
    class Meta:
        db_table = "crawl_campaign_items"
        unique_together = ("campaign", "code")

    campaign = models.ForeignKey(CrawlCampaign, on_delete=models.CASCADE)
    code = models.CharField(max_length=50, validators=[code_validate])
    parent_code = models.CharField(max_length=50, validators=[code_validate], null=True, blank=True)
    xpath = models.CharField(max_length=250)
    ignore_duplication = models.BooleanField(default=False)

    @property
    def childrens(self):
        return CrawlItem.objects.filter(parent_code=self.code, campaign=self.campaign).all()
