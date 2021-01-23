from datetime import datetime

from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from crawl_service.campaigns.scrapy_spider import NovelSpider
from crawl_service.models import CrawlCampaign


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        campaigns = CrawlCampaign.objects.filter(active=True, status='stopped').all()

        process = CrawlerProcess(get_project_settings())
        campaigns_update = []
        for cam in campaigns:
            run_able = ((datetime.now() - cam.last_run).total_seconds() / 60) >= cam.repeat_time
            if run_able:
                cam.status = 'running'
                cam.save()
                campaigns_update.append(cam)
                process.crawl(NovelSpider, campaign=cam)

        process.start()  # the script will block here until all crawling jobs are finished

        for cam in campaigns_update:
            cam.last_run = datetime.now()
            cam.status = 'stopped'
            cam.save()
