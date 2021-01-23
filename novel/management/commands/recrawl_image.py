from django.core.management.base import BaseCommand

from crawl_service import utils
from novel.models import Novel


class Command(BaseCommand):

    def full_schema_url(self, url, novel):
        if url.strip().startswith('//'):
            url = "http:" + url
        elif url.strip().startswith('/'):
            url = novel.campaign_source.homepage.strip('/') + url
        else:
            url = url.rstrip('/')

        return url

    def handle(self, *args, **kwargs):
        novels = Novel.objects.all()
        for novel in novels:
            if novel.thumbnail_image:
                thumbnail_image = self.full_schema_url(novel.thumbnail_image)
                utils.download_image(thumbnail_image, novel.slug,
                                     referer=novel.campaign_source.homepage)
