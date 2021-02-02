from django.db import models

# from crawl_service.campaigns.mapping import CampaignMapping, ActionMapping
from crawl_service import settings
from crawl_service.utils import code_validate


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
    campaign_type = models.CharField(max_length=50, choices=settings.CRAWL_TYPE_MAPPING.get(settings.APP_NAME))
    name = models.CharField(max_length=250)
    target_url = models.CharField(max_length=250)
    target_direct = models.BooleanField(default=True,
                                        help_text="If option is TRUE, this campaign will call directly by target_url "
                                                  "otherwise call via API and get list of urls from response.")
    next_page_xpath = models.CharField(max_length=250, null=True, blank=True, default='',
                                       help_text="Blank if no pagination.")
    paging_delay = models.IntegerField(default=0,
                                       help_text="If the target url has pagination, "
                                                 "this option will allow to delay any second after each request")
    no_update_limit = models.IntegerField(default=0, help_text="Default = 0 is no limit")
    repeat_time = models.IntegerField(default=5,
                                      help_text="Minutes to repeat this campaign, set 0 if dont want to repeat")
    last_run = models.DateTimeField(default=None, null=True, blank=True)
    run_synchonize = models.BooleanField(default=True)
    status = models.CharField(max_length=10, choices=CAMPAIGN_STATUS)
    active = models.BooleanField(default=True)

    @property
    def items(self):
        return CrawlItem.objects.filter(campaign=self).all()

    def full_clean(self, exclude=None, validate_unique=True):
        pass

    @property
    def actions(self):
        return CrawlItemAction.objects.filter(campaign=self).all()


class CrawlItem(models.Model):
    class Meta:
        db_table = "crawl_campaign_items"
        unique_together = ("campaign", "code")

    campaign = models.ForeignKey(CrawlCampaign, on_delete=models.CASCADE)
    code = models.CharField(max_length=50, validators=[code_validate])
    multi = models.BooleanField(default=False)
    xpath = models.CharField(max_length=250)
    child_xpath = models.CharField(max_length=250, help_text="Group all child item to one", null=True, blank=True)

    @property
    def actions(self):
        return CrawlItemAction.objects.filter(campaign=self.campaign, crawl_item_code=self.code).all()


class CrawlItemAction(models.Model):
    class Meta:
        db_table = "crawl_campaign_actions"

    campaign = models.ForeignKey(CrawlCampaign, on_delete=models.CASCADE)
    action = models.CharField(max_length=250, choices=settings.CRAWL_ACTION_MAPPING.get(settings.APP_NAME))
    params = models.CharField(max_length=250, blank=True, null=True)


class CrawlLog(models.Model):
    class Meta:
        db_table = "crawl_campaign_logs"
        ordering = ["-created_at"]

    campaign = models.ForeignKey(CrawlCampaign, on_delete=models.CASCADE)
    source_url = models.TextField(max_length=250, null=True, blank=True)
    crawled_data = models.JSONField(null=True, blank=True)
    log = models.JSONField(null=True, blank=True)

    # Datetime
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CDNServer(models.Model):
    class Meta:
        db_table = "cdn_server"
        ordering = ["name"]

    name = models.CharField(max_length=250, unique=True)
    server_id = models.CharField(max_length=250, blank=True, null=True)
    endpoint = models.CharField(max_length=250)

    active = models.BooleanField(default=True)
    status = models.CharField(max_length=10, choices=CAMPAIGN_STATUS)

    def __str__(self):
        return self.name

    @classmethod
    def get_cdn(cls):
        return cls.objects.first()

    @classmethod
    def get_available_cdn(cls):
        return cls.objects.filter(active=False, status='stopped').all()
