import zlib

from rest_framework import serializers

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
    type_name = 'NOVEL'
    model_class = Novel
    # List keys use to check value duplicate
    update_by_fields = ['name', 'url']

    def handle(self):
        if not NovelCampaignSchema(data=self.crawled_data).is_valid():
            raise Exception("Loi schema")

        values = self.crawled_data.get('story_wrap', [])
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
                    novel.url = self.handle_url(item.get("url") or "")

                    latest_chapter = item.get('latest_chapter_url')
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
                new_data.append(Novel(**item))

        if new_data:
            Novel.objects.bulk_create(new_data, ignore_conflicts=True)


class NovelChapterSerializer(serializers.Serializer):
    name = serializers.CharField()
    chapter_url = serializers.CharField()


class NovelInfoCampaignSchema(serializers.Serializer):
    url = serializers.CharField()
    status = serializers.CharField(required=False)
    authors = serializers.CharField(required=False)
    genres = serializers.CharField(required=False)
    descriptions = serializers.CharField(required=False)
    list_chapter = NovelChapterSerializer(many=True, required=False)


class NovelInfoCampaignType(BaseCrawlCampaignType):
    type_name = 'NOVEL_INFO'
    model_class = Novel
    update_by_fields = ['url']

    def handle(self):
        crawled_data = self.crawled_data
        if not NovelInfoCampaignSchema(data=crawled_data).is_valid():
            raise Exception("Loi schema")

        for update_field, novels in self.update_values.items():
            skey = crawled_data.get(update_field)
            if skey in novels.keys():
                novel = novels.get(skey)

                authors = crawled_data.get("authors") or []
                if isinstance(authors, str):
                    authors = [authors]

                for author in authors:
                    author, _ = Author.objects.get_or_create(name=author.title().strip())

                    novel.authors.add(author)

                genres = crawled_data.get("genres") or []
                if isinstance(genres, str):
                    genres = [genres]

                for genre in genres:
                    genre, _ = Genre.objects.get_or_create(name=genre.title().strip())
                    novel.genres.add(genre)

                for chapter in crawled_data.get("list_chapter") or []:
                    chapter, _ = NovelChapter.objects.get_or_create(name=chapter.get("name"),
                                                                    url=self.handle_url(chapter.get("chapter_url")),
                                                                    novel=novel)

                status = crawled_data.get("status")
                if status:
                    status, _ = Status.objects.get_or_create(name=status.title().strip())
                    novel.status = status

                descriptions = crawled_data.get("descriptions")
                if descriptions:
                    novel.descriptions = crawled_data.get("descriptions")

                novel.chapter_updated = True
                novel.save()
                break


class NovelChapterCampaignSchema(serializers.Serializer):
    url = serializers.CharField()
    content = serializers.CharField(required=False)


class NovelChapterCampaignType(BaseCrawlCampaignType):
    type_name = 'NOVEL_CHAPTER'
    model_class = NovelChapter
    update_by_fields = ['url']

    def handle(self):
        crawled_data = self.crawled_data
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
