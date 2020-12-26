from time import sleep

import requests
import scrapy

from crawl_service.campaigns.mapping import CampaignMapping
from crawl_service.models import CrawlCampaign


class NovelSpider(scrapy.Spider):

    def __init__(self, campaign: CrawlCampaign, **kwargs):
        self.campaign = campaign
        self.start_urls = [campaign.target_url]
        if not campaign.target_direct:
            res = requests.get(campaign.target_url, timeout=30)
            if res.status_code == 200:
                self.start_urls = res.json()

        self.temp_data = {}
        self.current_page = 1

        super().__init__(**kwargs)

    def parse(self, response, **kwargs):
        parent_items = self.campaign.parent_items
        res_data = {"url": response.url}
        for child_item in parent_items:
            _data = self.get_item_value(response, child_item)
            res_data.update(_data)

        campaign_type = CampaignMapping.type_mapping.get(self.campaign.campaign_type)
        campaign_type(res_data).handle()

        if self.campaign.paging_delay:
            sleep(self.campaign.paging_delay)

        if self.campaign.paging_param and res_data:
            self.current_page += 1
            next_page = "%s%s%s" % (self.start_urls[0], self.campaign.paging_param, self.current_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def load_redis_data(self):
        pass

    def get_item_value(self, response, item):
        res_data = {item.code: []}

        p_objects = response.xpath(item.xpath)
        if item.xpath.lower().endswith('all_text()'):
            text_arr = p_objects.extract()
            res_data[item.code] = "<p>%s</p>" % "</p><p>".join(txt.strip("\n ") for txt in text_arr if txt.strip("\n "))
        else:
            for p_obj in p_objects:
                childrens = item.childrens
                if not childrens:
                    res_data[item.code] = p_obj.extract() or None
                    continue

                res_item = {}
                for child_item in childrens:
                    item_val = self.get_item_value(p_obj, child_item)
                    if item_val.get(child_item.code):
                        res_item.update(item_val)

                res_data[item.code].append(res_item)

        if res_data.get(item.code):
            return res_data

        return {}

