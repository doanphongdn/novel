from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess

from crawl_service.models import CrawlCampaign
from novel.models import Novel


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        campaigns = CrawlCampaign.objects.filter(active=True)

        process = CrawlerProcess()
        for cam in campaigns:
            process.crawl(Novel, campaign=cam)

        process.start()  # the script will block here until all crawling jobs are finished
        pass
