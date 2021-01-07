from datetime import datetime

from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess

from crawl_service.campaigns.scrapy_spider import NovelSpider
from crawl_service.models import CrawlCampaign, CAMPAIGN_STATUS


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        campaigns = CrawlCampaign.objects.filter(active=True, status='stopped').all()

        process = CrawlerProcess()
        campaigns_update = []
        for cam in campaigns:
            run_able = ((datetime.now() - cam.last_run).total_seconds() / 60) >= cam.repeat_time
            if run_able:
                process.crawl(NovelSpider, campaign=cam)
                cam.status = 'running'
                cam.save()
                campaigns_update.append(cam)

        process.start()  # the script will block here until all crawling jobs are finished

        for cam in campaigns_update:
            cam.last_run = datetime.now()
            cam.status = 'stopped'
            cam.save()
