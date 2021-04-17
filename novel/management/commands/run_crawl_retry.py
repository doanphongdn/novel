from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db.models import Q

# from crawl_service.utils import query_debugger
from django_cms.utils.helpers import check_url, full_schema_url, get_referer
from novel.models import CrawlNovelRetry, NovelChapter, CDNNovelFile


class Command(BaseCommand):

    # @query_debugger
    def handle(self, *args, **kwargs):
        print('[Retry Crawl Novel] Starting...')
        try:
            # with transaction.atomic():
            # available_retrying = CrawlNovelRetry.objects.select_for_update().filter().all()[0:10]
            limit_time = datetime.now() - timedelta(minutes=30)
            available_retrying = CrawlNovelRetry.objects.filter(
                Q(is_processing=False) | Q(updated_at__lte=limit_time)
            ).all()[0:20]
            if not available_retrying:
                print('[Retry Crawl Novel] Not Found any Records for processing... Stopped!')

            print('[Retry Crawl Novel] Found %s records for processing...' % len(available_retrying))

            # Update processing to prevent the other queries
            for novel_retry in available_retrying:
                novel_retry.is_processing = True

            CrawlNovelRetry.objects.bulk_update(available_retrying, ['is_processing'])

            chapter_updated_list = []
            for retry in available_retrying:
                # cdn_files = CDNNovelFile.objects.select_related('chapter').filter(
                #     chapter__in=retry.novel.chapters).all()
                # cdn_files = CDNNovelFile.objects.filter(chapter__in=retry.novel.chapters).all()
                ids = CDNNovelFile.objects.filter(chapter__in=retry.novel.chapters).values_list('chapter', flat=True)
                for chapter in retry.novel.chapters.exclude(pk__in=set(ids)):
                    if chapter == retry.chapter:
                        continue
                    if not chapter.images_content:
                        continue
                    urls = [full_schema_url(img_url) for img_url in chapter.images_content.split("\n")]
                    if not len(urls):
                        continue
                    referer = get_referer(chapter)
                    if chapter and not check_url(urls[0], referer):
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
