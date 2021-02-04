from datetime import datetime

import os
from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from threading import Thread

from crawl_service.campaigns.scrapy_spider import NovelSpider
from crawl_service.models import CrawlCampaign

from scrapy.crawler import Crawler
from scrapy import signals
from twisted.internet import reactor
from billiard import Process


class CrawlerScript(Process):
    def __init__(self, spider):
        print("[%s] Crawler Running..." % spider.campaign.name)
        Process.__init__(self)
        settings = get_project_settings()
        self.crawler = Crawler(spider.__class__, settings)
        self.crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
        self.spider = spider
        self.campaign = spider.campaign
        self.campaign.status = 'running'
        self.campaign.save()

    def run(self):
        self.crawler.crawl(spider=self.spider, campaign=self.campaign)
        # self.crawler.start()
        reactor.run()


class CrawlerRunning:
    def __init__(self, cam):
        print("[%s] Starting campaign..." % cam.name)
        self.spider = NovelSpider(cam)
        self.crawler = CrawlerScript(self.spider)
        self.stopped = False

    def crawl_start(self):
        self.crawler.start()

    def crawl_join_async(self):
        # spider = NovelSpider()
        # crawler = CrawlerScript(spider, cam)
        self.crawler.join()

        self.crawler.campaign.last_run = datetime.now()
        self.crawler.campaign.status = 'stopped'
        self.crawler.campaign.save()
        self.stopped = True
        print("[%s] Finish campaign " % self.spider.campaign.name)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        ### Cach 1
        # campaigns = CrawlCampaign.objects.filter(active=True, status='stopped').all()
        #
        # process = CrawlerProcess(get_project_settings())
        # campaigns_update = []
        # for cam in campaigns:
        #     run_able = ((datetime.now() - cam.last_run).total_seconds() / 60) >= cam.repeat_time
        #     if run_able:
        #         print("[%s] Starting campaign... " % cam.name)
        #         cam.status = 'running'
        #         cam.save()
        #         campaigns_update.append(cam)
        #         process.crawl(NovelSpider, campaign=cam)
        #
        # process.start()  # the script will block here until all crawling jobs are finished
        #
        # for cam in campaigns_update:
        #     print("[%s] Finish campaign " % cam.name)
        #     cam.last_run = datetime.now()
        #     cam.status = 'stopped'
        #     cam.save()

        #### Cach 2
        # max_thread = int(os.environ.get('CAMPAIGNS_THREAD_NUM', 2))
        # running_campaigns_number = sum(1 for c in campaigns if c.status == 'running')
        # if max_thread <= running_campaigns_number:
        #     print("Max %s threads are running" % running_campaigns_number)
        #     return
        #
        # running_campaigns = []
        #
        # for cam in campaigns:
        #     if cam.status == 'running':
        #         running_campaigns.append(cam)
        #         continue
        #
        #     running_campaigns_number = sum(1 for c in running_campaigns if c.stopped == False)
        #     if running_campaigns_number >= max_thread:
        #         break
        #
        #     run_able = ((datetime.now() - cam.last_run).total_seconds() / 60) >= cam.repeat_time
        #     if run_able:
        #         crawl_running = CrawlerRunning(cam)
        #         crawl_running.crawl_start()
        #         running_campaigns.append(crawl_running)
        #
        # for crawl_running in running_campaigns:
        #     # Ignore type as CrawlCampaign added before
        #     if not isinstance(crawl_running, CrawlerRunning):
        #         continue
        #     crawl_running.crawl_join_async()
        #
        # if len(running_campaigns) >= max_thread:
        #     print("%s threads are running" % len(running_campaigns))

        ### Cach 3
        campaigns = CrawlCampaign.objects.filter(active=True).all()
        max_thread = int(os.environ.get('CAMPAIGNS_THREAD_NUM', 2))
        running_campaigns_number = sum(1 for c in campaigns if c.status == 'running')
        if max_thread <= running_campaigns_number:
            print("[Crawl Campaign Command] Max %s threads are running" % running_campaigns_number)
            return

        process = CrawlerProcess(get_project_settings())
        # campaigns_update = []
        threads = []
        for cam in campaigns:
            run_able = ((datetime.now() - cam.last_run).total_seconds() / 60) >= cam.repeat_time
            if not run_able:
                continue

            print("[%s] Starting campaign... " % cam.name)
            cam.status = 'running'
            cam.save()
            # campaigns_update.append(cam)
            process.crawl(NovelSpider, campaign=cam)

            if len(threads) + running_campaigns_number < max_thread:
                thread = Thread(target=process.start)
                thread.daemon = False  # Daemonize thread
                threads.append({'campaign': cam, 'thread': thread})

        for thread in threads:
            thread.get('thread').start()

        for thread in threads:
            thread.get('thread').join()

            cam = thread.get('campaign')
            if not cam:
                continue
            print("[%s] Finish campaign. " % cam.name)
            cam.last_run = datetime.now()
            cam.status = 'stopped'
            cam.save()
