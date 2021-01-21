import json
from time import sleep

import requests
import scrapy

from crawl_service.campaigns.mapping import CampaignMapping, ActionMapping
from crawl_service.models import CrawlCampaign


class NovelSpider(scrapy.Spider):
    def __init__(self, campaign: CrawlCampaign, **kwargs):
        self.campaign = campaign
        self.start_urls = []
        self.other_urls = []
        self.prefetch_by_data = None

        if not campaign.target_direct:
            res = requests.get(campaign.target_url, timeout=30)
            if res.status_code == 200:
                data = res.json()
                if data:
                    self.prefetch_by_data = {"url": [d for d in data]}
                    if data and self.campaign.run_synchonize:
                        self.start_urls = data
                    elif data:
                        self.start_urls = [data.pop(0)]
                        self.other_urls = data or []
        else:
            self.start_urls = [campaign.target_url]

        campaign_mapping = CampaignMapping.get_mapping(self.campaign.campaign_type)
        self.campaign_type = campaign_mapping(self.campaign, self.prefetch_by_data)

        super().__init__(name=campaign.name, **kwargs)

    def parse(self, response, **kwargs):
        paging = kwargs.get('paging') or False
        origin_url = kwargs.get('origin_url') if paging else response.url.rstrip('/')

        res_data = {"url": origin_url}
        for item in self.campaign.items:
            _data = self.get_item_value(response, item)
            res_data.update(_data)

        for act in self.campaign.actions:
            action = ActionMapping.get_mapping(act.action)
            try:
                params = json.loads(act.params)
                res_data = action.handle(res_data, **params)
            except:
                pass

        continue_paging = self.campaign_type.handle(res_data, self.campaign,
                                                    no_update_limit=self.campaign.no_update_limit)

        if self.campaign.paging_delay:
            sleep(self.campaign.paging_delay)

        if self.campaign.next_page_xpath and res_data and continue_paging:
            next_page = response.xpath(self.campaign.next_page_xpath).get() or ""
            next_page = self.campaign_type.full_schema_url(next_page)

            yield scrapy.Request(next_page, cb_kwargs={'origin_url': origin_url, 'paging': True},
                                 callback=self.parse)
        elif self.other_urls:
            url = self.other_urls.pop(0)
            yield scrapy.Request(url, cb_kwargs={'origin_url': url, 'paging': False}, callback=self.parse)

    @staticmethod
    def get_item_value(response, item):
        p_object = response.xpath(item.xpath)
        if item.child_xpath:
            item_value = []
            for obj in p_object:
                objs = obj.xpath(item.child_xpath).getall()
                value = "".join(objs)
                item_value.append(value)
        else:
            item_value = p_object.getall() if item.multi else p_object.get()

        if item_value:
            item_value = [str(val).replace("\x00", "") for val in item_value] \
                if isinstance(item_value, list) else str(item_value).replace("\x00", "")
            return {item.code: item_value}

        return {}
