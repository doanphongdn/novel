import os
import zlib

from rest_framework import serializers

from crawl_service.campaigns.base import BaseCrawlCampaignType
from crawl_service import utils, settings
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

    def handle(self, crawled_data):
        if not NovelCampaignSchema(data=crawled_data).is_valid():
            raise Exception("Loi schema")

        values = crawled_data.get('novel_block', [])
        new_data = []
        no_update_limit = 10
        no_update_count = 0

        for item in values:
            exist = False
            for update_field, novel_list in self.update_values.items():
                skey = item.get(update_field)
                if skey in novel_list.keys():
                    novel = novel_list.get(skey)
                    novel.name = item.get("name")
                    novel.url = self.full_schema_url(item.get("url") or "")

                    latest_chapter = self.full_schema_url(item.get('latest_chapter_url') or "")
                    if latest_chapter:
                        novel_chapters = novel.chapters.values_list('url', flat=True)
                        if latest_chapter not in novel_chapters:
                            novel.chapter_updated = False
                            no_update_count = 0
                        else:
                            novel.chapter_updated = True
                            no_update_count += 1

                    novel.save()
                    exist = True
                    break

            if no_update_count >= no_update_limit:
                # TODO: raise error if want to handle latest update
                pass

            if not exist:
                for url in ['url', 'latest_chapter_url']:
                    if item.get(url):
                        item[url] = self.full_schema_url(item[url] or "")

                new_data.append(Novel(**item))

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

    def handle(self, crawled_data):
        if not NovelInfoCampaignSchema(data=crawled_data).is_valid():
            raise Exception("Loi schema")

        continue_paging = True
        for update_field, novels in self.update_values.items():
            skey = crawled_data.get(update_field)
            if skey in novels.keys():
                novel = novels.get(skey)
                update = False

                thumbnail_image = crawled_data.get('thumbnail_image')
                if not novel.thumbnail_image and thumbnail_image:
                    thumbnail_image = self.full_schema_url(thumbnail_image)
                    local_image = utils.download_image(thumbnail_image, novel.slug,
                                                       referer=self.campaign.campaign_source.homepage)

                    novel.thumbnail_image = local_image or thumbnail_image
                    update = True

                if not novel.authors:
                    authors = crawled_data.get("authors") or []
                    for author in authors:
                        author, _ = Author.objects.get_or_create(name=author.title().strip())
                        novel.authors.add(author)
                        update = True

                if not novel.genres:
                    genres = crawled_data.get("genres") or []
                    for genre in genres:
                        genre, _ = Genre.objects.get_or_create(name=genre.title().strip())
                        novel.genres.add(genre)
                        update = True

                chapters = []
                for chapter in crawled_data.get("list_chapter") or []:
                    chapter_url = self.full_schema_url(chapter.get("chapter_url"))
                    chapters.append(NovelChapter(novel=novel,
                                                 name=chapter.get("name"),
                                                 url=chapter_url))
                    if chapter_url == novel.latest_chapter_url:
                        continue_paging = False

                if chapters:
                    NovelChapter.objects.bulk_create(chapters, ignore_conflicts=True)
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
                    novel.chapter_updated = True
                    novel.save()

        return continue_paging


class NovelChapterCampaignSchema(serializers.Serializer):
    url = serializers.CharField()
    content = serializers.CharField(required=False)


class NovelChapterCampaignType(BaseCrawlCampaignType):
    name = 'NOVEL_CHAPTER'
    model_class = NovelChapter
    update_by_fields = ['url']

    def handle(self, crawled_data):
        if not NovelChapterCampaignSchema(data=crawled_data).is_valid():
            raise Exception("Loi schema")

        for update_field, chapters in self.update_values.items():
            crawled_value = crawled_data.get(update_field)
            if crawled_value in chapters.keys():
                chapter = chapters.get(crawled_value)
                chapter_content = crawled_data.get("content")
                if chapter_content:
                    compressed = zlib.compress(chapter_content.encode())
                    chapter.binary_content = compressed
                    chapter.content_updated = True
                    chapter.save()
