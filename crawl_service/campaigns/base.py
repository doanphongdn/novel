from functools import reduce
from operator import or_

from django.db.models import Q


class BaseCrawlCampaignType(object):
    name = "base"
    model_class = None
    update_by_fields = []

    def __init__(self, campaign):
        self.campaign = campaign
        # self.update_values = {}
        # if self.update_by_fields:
        #     self.update_values = {f: {} for f in self.update_by_fields}
        #     objects = self.model_class.objects.all()
        #     for obj in objects:
        #         for key, value in self.update_values.items():
        #             val = getattr(obj, key, None)
        #             if val:
        #                 value[val] = obj

    def build_condition_or(self, item):
        return reduce(or_, (Q(**{field + "__in": item.get(field)}) for field in self.update_by_fields))

    def full_schema_url(self, url):
        if not url.startswith("http"):
            if url.startswith('//'):
                return "http:%s" % url.rstrip('/')
            elif url.startswith('/'):
                return "%s%s" % (self.campaign.campaign_source.homepage.strip('/'), url.rstrip('/'))
        else:
            return url.rstrip('/')

    def handle(self, crawled_data):
        return True


class BaseAction(object):
    name = "base_action"

    @classmethod
    def handle(cls, obj, *args, **kwargs):
        pass
