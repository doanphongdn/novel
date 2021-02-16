from django.core.management.base import BaseCommand
from django.db import transaction

from crawl_service import utils
# from crawl_service.utils import query_debugger
from novel.models import CrawlNovelRetry, NovelChapter


class Command(BaseCommand):

    # @query_debugger
    def handle(self, *args, **kwargs):
        print('[Retry Crawl Novel] Starting...')
        try:
            with transaction.atomic():
                available_retrying = CrawlNovelRetry.objects.select_for_update().filter().all()[0:10]
                if not available_retrying:
                    print('[Retry Crawl Novel] Not Found any Records for processing... Stopped!')

                print('[Retry Crawl Novel] Found %s records for processing...' % len(available_retrying))

                chapter_updated_list = []
                for retry in available_retrying:
                    for chapter in retry.novel.chapters:
                        if chapter == retry.chapter:
                            continue
                        urls = [utils.full_schema_url(img_url) for img_url in chapter.images_content.split("\n")]
                        if not len(urls):
                            continue
                        referer = utils.get_referer(chapter)
                        if chapter and not utils.check_url(urls[0], referer):
                            chapter.chapter_updated = False
                            chapter_updated_list.append(chapter)
                    retry.delete()

                if chapter_updated_list:
                    NovelChapter.objects.bulk_update(chapter_updated_list, ['chapter_updated'])
                    print('[Retry Crawl Novel] Found %s records to change chapter_updated...'
                          % len(chapter_updated_list))

        except Exception as e:
            print("[Retry Crawl Novel] Error: %s" % e)

        print('[Retry Crawl Novel] Finish')
