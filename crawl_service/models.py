from django.db import models

from django.core.exceptions import ValidationError
import re

from django.db.models import Q


def code_validate(value):
    reg = re.compile('^[a-zA-Z0-9_]+$')
    if not reg.match(value):
        raise ValidationError(u'<%s> must be character, number or underline' % value)


class CrawlSource(models.Model):
    class Meta:
        db_table = "crawl_source"

    code = models.CharField(max_length=50, validators=[code_validate])
    name = models.CharField(max_length=250)
    homepage = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class CrawlCampaign(models.Model):
    class Meta:
        db_table = "crawl_campaigns"

    source = models.ForeignKey(CrawlSource, on_delete=models.CASCADE)
    code = models.CharField(max_length=50, validators=[code_validate])
    name = models.CharField(max_length=250)
    source_url = models.CharField(max_length=250, help_text="HTTP url or use format [campaign_code].[item_code] "
                                                            "to get urls from campaign parent")
    page_limit = models.IntegerField(default=0, help_text="Set 0 want for dynamic redirect page with page param name.")
    page_param_name = models.CharField(max_length=50, null=True, blank=True, default='',
                                       help_text="Blank if no pagination.")
    api_url = models.CharField(max_length=250, null=True, blank=True,
                               help_text="API receive data from campaign with method POST")
    active = models.BooleanField(default=True)

    @property
    def child_items(self):
        return CrawlItem.objects.filter(parent_code__isnull=False, campaign=self).exclude(parent_code=None).all()

    @property
    def parent_items(self):
        return CrawlItem.objects.filter(Q(parent_code=None) | Q(parent_code__isnull=True), campaign=self).all()

    @property
    def conditions(self):
        return CrawlCondition.objects.filter(campaign=self).all()


CRAWL_FUNCTIONS = [
    ('md5', "MD5")
]


class CrawlItem(models.Model):
    class Meta:
        db_table = "crawl_campaign_items"
        unique_together = ("campaign", "parent_code", "code")

    campaign = models.ForeignKey(CrawlCampaign, on_delete=models.CASCADE)
    parent_code = models.CharField(max_length=50, null=True, blank=True)
    code = models.CharField(max_length=50, validators=[code_validate])
    xpath = models.CharField(max_length=250)
    xpath_property = models.CharField(max_length=50, null=True, blank=True,
                                      help_text="@src, @href, text(), html(). Blank if parent item.")
    ignore_duplicate = models.BooleanField(default=False)

    @property
    def childrens(self):
        return CrawlItem.objects.filter(parent_code=self.code, campaign=self.campaign).all()

    @property
    def parent_item(self):
        return CrawlItem.objects.filter(code=self.parent_code, campaign=self.campaign).first()

    @property
    def full_item_code(self):
        parent = self.parent_item
        if not parent:
            return self.code
        else:
            return "%s/%s" % (parent.full_item_code, self.code)

    def __str__(self):
        return "Code: %s" % self.code


CRAWL_CONDITION_ACTIONS = [
    ('check_dupplicate', 'CHECK DUPLICATE'),
]


class CrawlCondition(models.Model):
    class Meta:
        db_table = "crawl_campaign_conditions"

    campaign = models.ForeignKey(CrawlCampaign, on_delete=models.CASCADE)
    item_code = models.CharField(max_length=50)
    action = models.CharField(max_length=50, choices=CRAWL_CONDITION_ACTIONS)
    params = models.CharField(max_length=250, default='')

    @property
    def item(self):
        return CrawlItem.objects.filter(code=self.item_code, campaign=self.campaign).first()

    def __str__(self):
        return "Id: %s" % str(self.id)
