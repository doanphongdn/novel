from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess

from crawl_service.campaigns.scrapy_spider import NovelSpider
from crawl_service.models import CrawlCampaign


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        campaigns = CrawlCampaign.objects.filter(active=True)

        process = CrawlerProcess()
        for cam in campaigns:
            process.crawl(NovelSpider, campaign=cam)

        process.start()  # the script will block here until all crawling jobs are finished
        pass
