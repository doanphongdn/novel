import scrapy
from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess

from crawl_service.models import CrawlCampaign
from lxml import etree


class MySpider1(scrapy.Spider):
    campaign = None
    res_data = None

    def __init__(self, campaign: CrawlCampaign, **kwargs):
        self.campaign = campaign
        self.start_urls = [campaign.source_url]

        super().__init__(self.campaign.code, **kwargs)

    def _parse(self, response, **kwargs):
        items = self.campaign.items
        res_data = {}
        for i in items:
            res_data.update(self.get_item_value(response, i))

        yield res_data

    def get_item_value(self, response, item):
        res_data = {item.code: []}
        p_objects = response.xpath(item.xpath)
        for p_obj in p_objects:
            childrens = item.childrens
            if not childrens and item.xpath_property:
                if item.xpath_property.lower() == 'html()':
                    values = [etree.tounicode(p_obj.root)]
                else:
                    values = p_obj.xpath(item.xpath_property).extract() or None

                if values and len(values) == 1:
                    res_data[item.code] = values[0]
                else:
                    res_data[item.code] = values

                continue

            res_item = {}
            for child_item in childrens:
                res_item.update(self.get_item_value(p_obj, child_item))

            if len(res_item) == 1:
                res_data[item.code] = res_item
            else:
                res_data[item.code].append(res_item or None)

        return res_data


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        campaigns = CrawlCampaign.objects.all()

        process = CrawlerProcess()
        for cam in campaigns:
            process.crawl(MySpider1, campaign=cam)

        abc = process.start()  # the script will block here until all crawling jobs are finished
        pass
