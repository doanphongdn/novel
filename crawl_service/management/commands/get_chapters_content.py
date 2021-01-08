from datetime import datetime

from django.core.management.base import BaseCommand
from django.db.models import Max
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from crawl_service.campaigns.scrapy_spider import NovelSpider
from crawl_service.models import CrawlCampaign
from novel.models import NovelChapter


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        campaigns = CrawlCampaign.objects.filter(active=True, status='stopped').all()

        while True:
            process = CrawlerProcess(get_project_settings())
            campaigns_update = []
            for cam in campaigns:
                # run_able = ((datetime.now() - cam.last_run).total_seconds() / 60) >= cam.repeat_time
                # if run_able:
                process.crawl(NovelSpider, campaign=cam)
                cam.status = 'running'
                cam.save()
                # campaigns_update.append(cam)

            process.start()  # the script will block here until all crawling jobs are finished

            content_update = NovelChapter.objects.filter(content_updated=False).aggregate(Max('id'))
            if not content_update.get('id__max') or content_update.get('id__max') == 0:
                return
