from django.core.management.base import BaseCommand

from crawl_service import utils
# from crawl_service.utils import query_debugger
from novel.models import CrawlNovelRetry, NovelChapter


class Command(BaseCommand):

    # @query_debugger
    def handle(self, *args, **kwargs):
        print('[Retry Crawl New Novel] Starting...')
        try:
            available_chapters = NovelChapter.objects.filter(active=True, chapter_updated=True,
                                                             crawlnovelretry=None).order_by(
                "-created_at").all()[0:12]
            if not available_chapters:
                print('[Retry Crawl New Novel] Not Found any Records for processing... Stopped!')

            print('[Retry Crawl New Novel] Found %s records for processing...' % len(available_chapters))

            chapter_updated_list = []
            for chapter in available_chapters:
                urls = chapter.images
                if not len(urls):
                    continue
                referer = utils.get_referer(chapter)
                if chapter and chapter not in chapter_updated_list and not utils.check_url(
                        utils.full_schema_url(urls[0]), referer):
                    chapter.chapter_updated = False
                    CrawlNovelRetry.create_crawl_retry(chapter)
                    chapter_updated_list.append(chapter)

            if chapter_updated_list:
                NovelChapter.objects.bulk_update(chapter_updated_list, ['chapter_updated'])
                print('[Retry Crawl New Novel] Found %s records to change chapter_updated...'
                      % len(chapter_updated_list))

        except Exception as e:
            print("[Retry Crawl New Novel] Error: %s" % e)

        print('[Retry Crawl New Novel] Finish')
