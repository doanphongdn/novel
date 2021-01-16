import os
import zlib
from time import sleep

from rest_framework import serializers

from crawl_service import utils
from crawl_service.campaigns.base import BaseCrawlCampaignType
from novel.models import Author, Genre, Status, NovelChapter, Novel


class NovelSerializer(serializers.Serializer):
    name = serializers.CharField()
    url = serializers.CharField()
    latest_chapter_url = serializers.CharField(required=False)
    thumbnail_image = serializers.CharField(required=False)


class NovelCampaignSchema(serializers.Serializer):
    novel_block = NovelSerializer(many=True)


class NovelCampaignType(BaseCrawlCampaignType):
    name = 'NOVEL'
    model_class = Novel
    # List keys use to check value duplicate
    update_by_fields = ['name', 'url']

    def handle(self, crawled_data, *args, **kwargs):
        if not NovelCampaignSchema(data=crawled_data).is_valid():
            raise Exception("Loi schema")

        values = crawled_data.get('novel_block', [])
        new_data = []
        no_update_count = 0
        no_update_limit = kwargs.get('no_update_limit') or 0

        for item in values:
            sleep(0.01)

            novel = self.model_class.objects.filter(self.build_condition_or(item)).first()
            if novel:
                novel.name = item.get("name")
                novel.url = self.full_schema_url(item.get("url") or "")

                latest_chapter = self.full_schema_url(item.get('latest_chapter_url') or "")
                if latest_chapter:
                    if latest_chapter != novel.latest_chapter_url:
                        novel.latest_chapter_url = latest_chapter
                        novel.novel_updated = False
                        no_update_count = 0
                    else:
                        novel.novel_updated = True
                        no_update_count += 1

                novel.save()
            else:
                for url in ['url', 'latest_chapter_url']:
                    if item.get(url):
                        item[url] = self.full_schema_url(item[url] or "")

                new_data.append(Novel(**item))

            if 0 < no_update_limit <= no_update_count:
                return False

        if new_data:
            Novel.objects.bulk_create(new_data, ignore_conflicts=True)

        return True


class NovelChapterSerializer(serializers.Serializer):
    name = serializers.CharField()
    chapter_url = serializers.CharField()


class NovelInfoCampaignSchema(serializers.Serializer):
    url = serializers.CharField()
    thumbnail_image = serializers.CharField(required=False)
    status = serializers.CharField(required=False)
    authors = serializers.ListField(required=False)
    genres = serializers.ListField(required=False)
    descriptions = serializers.CharField(required=False)
    list_chapter = NovelChapterSerializer(many=True, required=False)


class NovelInfoCampaignType(BaseCrawlCampaignType):
    name = 'NOVEL_INFO'
    model_class = Novel
    update_by_fields = ['url']

    def handle(self, crawled_data, *args, **kwargs):
        if not NovelInfoCampaignSchema(data=crawled_data).is_valid():
            raise Exception("Loi schema")

        continue_paging = True
        for field in self.update_by_fields:
            sleep(0.01)

            novel = self.update_values.get(field, {}).get(crawled_data.get(field))
            if not novel:
                continue

            update = False

            thumbnail_image = crawled_data.get('thumbnail_image')
            if not novel.thumbnail_image and thumbnail_image:
                thumbnail_image = self.full_schema_url(thumbnail_image)
                local_image = utils.download_image(thumbnail_image, novel.slug,
                                                   referer=self.campaign.campaign_source.homepage)

                novel.thumbnail_image = local_image or thumbnail_image
                update = True

            if not novel.authors.first():
                authors = crawled_data.get("authors") or []
                for author in authors:
                    author, _ = Author.objects.get_or_create(name=author.title().strip())
                    novel.authors.add(author)
                    update = True

            if not novel.genres.first():
                genres = crawled_data.get("genres") or []
                for genre in genres:
                    genre, _ = Genre.objects.get_or_create(name=genre.title().strip())
                    novel.genres.add(genre)
                    update = True

            chapters = {self.full_schema_url(chapter.get("chapter_url")): chapter.get("name")
                        for chapter in crawled_data.get("list_chapter") or []}

            if chapters:
                exist_chapters = NovelChapter.objects.filter(url__in=list(chapters.keys()))
                for ex_chap in exist_chapters:
                    ex_chap.name = chapters.pop(ex_chap.url)
                    ex_chap.save()

                new_chapters = [NovelChapter(novel=novel, name=name, url=url) for url, name in chapters.items()]
                if new_chapters:
                    NovelChapter.objects.bulk_create(new_chapters, ignore_conflicts=True)
                    update = True

            status = crawled_data.get("status")
            if status and status != novel.status:
                status, _ = Status.objects.get_or_create(name=status.title().strip())
                novel.status = status
                update = True

            descriptions = crawled_data.get("descriptions")
            if not novel.descriptions and descriptions:
                novel.descriptions = crawled_data.get("descriptions")
                update = True

            if update:
                novel.novel_updated = True
                novel.save()

        return continue_paging


class NovelChapterCampaignSchema(serializers.Serializer):
    url = serializers.CharField()
    content_text = serializers.CharField(required=False)
    content_images = serializers.ListField(required=False)


class NovelChapterCampaignType(BaseCrawlCampaignType):
    name = 'NOVEL_CHAPTER'
    model_class = NovelChapter
    update_by_fields = ['url']

    def handle(self, crawled_data, *args, **kwargs):
        if not NovelChapterCampaignSchema(data=crawled_data).is_valid():
            raise Exception("Loi schema")

        for field in self.update_by_fields:
            sleep(0.01)

            chapter = self.update_values.get(field, {}).get(crawled_data.get(field))
            if not chapter:
                continue

            content_text = crawled_data.get("content_text")
            if content_text:
                compressed = zlib.compress(content_text.encode())
                chapter.binary_content = compressed
                chapter.chapter_updated = True
                chapter.save()

            content_images = crawled_data.get("content_images")
            if content_images:
                chapter.images_content = '\n'.join(content_images)
                chapter.chapter_updated = True
                chapter.save()

        return True
