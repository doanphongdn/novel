from datetime import datetime

import os
from django.core.management.base import BaseCommand
# from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from crawl_service.campaigns.scrapy_spider import NovelSpider
from crawl_service.models import CrawlCampaign

from scrapy.crawler import Crawler
from scrapy import signals
# from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
from billiard import Process

class CrawlerScript(Process):
    def __init__(self, spider, cam):
        print("[%s] Crawler Running...", cam.name)
        Process.__init__(self)
        settings = get_project_settings()
        self.crawler = Crawler(spider.__class__, settings)
        self.crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
        self.spider = spider
        self.campaign = cam
        self.campaign.status = 'running'
        self.campaign.save()

    def run(self):
        self.crawler.crawl(self.spider, self.campaign)
        reactor.run()


class CrawlerRunning:
    def __init__(self, cam):
        self.spider = NovelSpider(cam)
        self.crawler = CrawlerScript(self.spider, cam)
        self.stopped = False

    def crawl_async(self):
        # spider = NovelSpider()
        # crawler = CrawlerScript(spider, cam)
        self.crawler.start()
        self.crawler.join()

        self.spider.campaign.last_run = datetime.now()
        self.spider.campaign.status = 'stopped'
        self.spider.campaign.save()
        self.stopped = True
        print("[%s] Finish campaign ", self.spider.campaign.name)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        campaigns = CrawlCampaign.objects.filter(active=True).all()

        # process = CrawlerProcess(get_project_settings())
        # campaigns_update = []
        # for cam in campaigns:
        #     run_able = ((datetime.now() - cam.last_run).total_seconds() / 60) >= cam.repeat_time
        #     if run_able:
        #         cam.status = 'running'
        #         cam.save()
        #         campaigns_update.append(cam)
        #         process.crawl(NovelSpider, campaign=cam)
        #
        # process.start()  # the script will block here until all crawling jobs are finished
        #
        # for cam in campaigns_update:
        #     cam.last_run = datetime.now()
        #     cam.status = 'stopped'
        #     cam.save()

        max_thread = int(os.environ.get('CAMPAIGNS_THREAD_NUM', 2))
        running_campaigns_number = sum(1 for c in campaigns if c.status == 'running')
        if max_thread <= running_campaigns_number:
            print("Max thread %s is running", running_campaigns_number)
            return

        running_campaigns = []

        for cam in campaigns:
            print("[%s] Starting campaign...", cam.name)
            if cam.status == 'running':
                running_campaigns.append(cam)
                continue

            running_campaigns_number = sum(1 for c in running_campaigns if c.status == 'running')
            if running_campaigns_number >= max_thread:
                break

            run_able = ((datetime.now() - cam.last_run).total_seconds() / 60) >= cam.repeat_time
            if run_able:
                crawl_running = CrawlerRunning(cam)
                crawl_running.crawl_async()
                running_campaigns.append(crawl_running)

