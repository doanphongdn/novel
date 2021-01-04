import re

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from crawl_service.campaigns.mapping import CampaignMapping, ActionMapping


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


CAMPAIGN_STATUS = [
    ('running', 'RUNNING'),
    ('stopped', 'STOPPED'),
]


class CrawlCampaign(models.Model):
    class Meta:
        db_table = "crawl_campaigns"

    campaign_source = models.ForeignKey(CrawlCampaignSource, on_delete=models.CASCADE)
    campaign_type = models.CharField(max_length=50, choices=CampaignMapping.list_types)
    name = models.CharField(max_length=250)
    target_url = models.CharField(max_length=250)
    target_direct = models.BooleanField(default=True,
                                        help_text="If option is TRUE, this campaign will call directly by target_url "
                                                  "otherwise call via API and get list of urls from response.")
    paging_param = models.CharField(max_length=50, null=True, blank=True, default='',
                                    help_text="Blank if no pagination.")
    paging_delay = models.IntegerField(default=0,
                                       help_text="If the target url has pagination, "
                                                 "this option will allow to delay any second after each request")
    repeat_time = models.IntegerField(default=5,
                                      help_text="Minutes to repeat this campaign, set 0 if dont want to repeat")
    last_run = models.DateTimeField(default=None, null=True, blank=True)
    status = models.CharField(max_length=10, choices=CAMPAIGN_STATUS)
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
        unique_together = ("campaign", "code", "parent_code")

    campaign = models.ForeignKey(CrawlCampaign, on_delete=models.CASCADE)
    code = models.CharField(max_length=50, validators=[code_validate])
    parent_code = models.CharField(max_length=50, validators=[code_validate], null=True, blank=True)
    xpath = models.CharField(max_length=250)

    @property
    def childrens(self):
        return CrawlItem.objects.filter(parent_code=self.code, campaign=self.campaign).all()

    @property
    def actions(self):
        return CrawlItemAction.objects.filter(campaign=self.campaign, crawl_item_code=self.code).all()


class CrawlItemAction(models.Model):
    class Meta:
        db_table = "crawl_campaign_actions"

    campaign = models.ForeignKey(CrawlCampaign, on_delete=models.CASCADE)
    crawl_item_code = models.CharField(max_length=250)
    action = models.CharField(max_length=250, choices=ActionMapping.list_types)
    params = models.CharField(max_length=250, blank=True, null=True)
