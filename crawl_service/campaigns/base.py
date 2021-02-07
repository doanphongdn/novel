from functools import reduce
from operator import or_

from django.db.models import Q

from crawl_service.models import CrawlLog


class BaseCrawlCampaignType(object):
    schema_class = None
    name = "base"
    model_class = None
    update_by_fields = []
    mapping_fields = {}

    def __init__(self, campaign, prefetch_by_data=None):
        self.campaign = campaign
        self.update_values = {}
        if prefetch_by_data and self.update_by_fields:
            exists_data = self.model_class.objects.filter(self.build_condition_or(prefetch_by_data)).all()

            self.update_values = {f: {} for f in self.update_by_fields}
            for obj in exists_data:
                for key, value in self.update_values.items():
                    val = getattr(obj, key, None)
                    if val:
                        value[val] = obj

    def build_condition_or(self, item):
        conditions = []
        for field in self.update_by_fields:
            item_value = item.get(self.mapping_fields.get(field, field))
            conditions.append(Q(**{field + "__in": item_value if isinstance(item_value, list) else [item_value]}))

        return reduce(or_, set(conditions))

    def full_schema_url(self, url):
        if url.strip().startswith('//'):
            url = "http:" + url
        elif url.strip().startswith('/'):
            url = self.campaign.src_campaign.homepage.strip('/') + url
        else:
            url = url.rstrip('/')

        return url

    def handle(self, crawled_data, campaign, *args, **kwargs):
        schema = self.schema_class(data=crawled_data)
        schema.is_valid()
        errors = schema.errors
        if errors:
            CrawlLog.objects.create(campaign=campaign,
                                    source_url=crawled_data.get("url"),
                                    crawled_data=crawled_data, log=dict(errors))

        return True


class BaseAction(object):
    name = "base_action"

    @classmethod
    def handle(cls, obj, *args, **kwargs):
        pass
