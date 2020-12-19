import scrapy
from django.core.management.base import BaseCommand
from lxml import etree
from parsel import SelectorList
from scrapy.crawler import CrawlerProcess

from crawl_service.models import CrawlCampaign
from crawl_service.services.campaign_type import CrawlCampaignType


class MySpider1(scrapy.Spider):

    def __init__(self, campaign: CrawlCampaign, **kwargs):
        self.campaign = campaign
        self.start_urls = [campaign.target_url]
        self.temp_data = {}
        self.current_page = 1

        super().__init__("aaaaaa", **kwargs)

    def parse(self, response, **kwargs):
        parent_items = self.campaign.parent_items
        res_data = {}
        for child_item in parent_items:
            res_data = self.get_item_value(response, child_item)

        # TODO: call api

        campaign_type = CrawlCampaignType.type_mapping.get(self.campaign.campaign_type)
        campaign_type(**res_data).handle()

        # if self.campaign.page_param_name and (
        #         self.campaign.page_limit <= 0 or self.current_page < self.campaign.page_limit) and res_data:
        #     self.current_page += 1
        #     next_page = "%s?%s=%s" % (self.start_urls[0], self.campaign.page_param_name, self.current_page)
        #     yield scrapy.Request(next_page, callback=self.parse)

    def load_redis_data(self):
        pass

    def get_item_value(self, response, item):
        html = False
        res_data = {item.code: []}
        if item.xpath.lower().endswith('html()'):
            html = True
            item.xpath = item.xpath[:-6]

        p_objects = response.xpath(item.xpath)
        for p_obj in p_objects:
            childrens = item.childrens
            if not childrens:
                if html:
                    value = [etree.tounicode(p_obj.root)]
                else:
                    if isinstance(p_obj, SelectorList):
                        value = p_obj.extract_first() or None
                    else:
                        value = p_obj.extract() or None

                res_data[item.code] = value

                continue

            res_item = {}
            for child_item in childrens:
                item_val = self.get_item_value(p_obj, child_item)
                if item_val.get(child_item.code):
                    res_item.update(item_val)

            if len(res_item) == 1:
                res_data[item.code] = res_item
            elif res_item:
                res_data[item.code].append(res_item)

        if res_data.get(item.code):
            return res_data

        return {}


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        campaigns = CrawlCampaign.objects.filter(active=True)

        process = CrawlerProcess()
        for cam in campaigns:
            process.crawl(MySpider1, campaign=cam)

        abc = process.start()  # the script will block here until all crawling jobs are finished
        pass
