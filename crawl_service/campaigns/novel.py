import zlib
from datetime import datetime
from time import sleep

from rest_framework import serializers

from crawl_service import utils
from crawl_service.campaigns.base import BaseCrawlCampaignType
from novel.models import Author, Genre, Status, NovelChapter, Novel, NovelFlat


class NovelSerializer(serializers.Serializer):
    name = serializers.CharField()
    url = serializers.CharField()
    latest_chapter_url = serializers.CharField(required=False)
    thumbnail_image = serializers.CharField(required=False)


class NovelCampaignSchema(serializers.Serializer):
    novel_block = NovelSerializer(many=True)


class NovelCampaignType(BaseCrawlCampaignType):
    schema_class = NovelCampaignSchema
    name = 'NOVEL'
    model_class = Novel
    # List keys use to check value duplicate
    update_by_fields = ['name', 'src_url']

    def handle(self, crawled_data, campaign, *args, **kwargs):
        continue_paging = super().handle(crawled_data, campaign, *args, **kwargs)

        values = crawled_data.get('novel_block', [])
        new_data = []
        no_update_count = 0
        no_update_limit = kwargs.get('no_update_limit') or 0

        for item in values:
            sleep(0.01)
            # replace field to storage in db
            item['src_url'] = item.pop('url', '').rstrip("/")
            item['name'] = item.get('name', '').lower().title()
            item['src_latest_chapter_url'] = item.pop('latest_chapter_url', '').rstrip("/")

            novel = self.model_class.objects.filter(self.build_condition_or(item)
                                                    ).prefetch_related('novel_flat').first()
            if novel:
                update = False
                src_latest_chap_url = self.full_schema_url(item.get('src_latest_chapter_url') or "")
                if src_latest_chap_url:
                    db_src_url = novel.novel_flat and novel.novel_flat.latest_chapter.get("source_url") or None
                    need_updated = src_latest_chap_url not in (novel.src_latest_chapter_url, db_src_url)
                    if need_updated and novel.novel_updated:
                        novel.src_latest_chapter_url = src_latest_chap_url
                        novel.novel_updated = False
                        update = True

                    no_update_count = int(not need_updated)
                if novel.src_url != item['src_url']:
                    novel.src_url = item['src_url']
                    update = True
                if novel.name.lower() != item["name"].lower():
                    novel.name = item["name"]
                    update = True

                if update:
                    # bypass duplicate name
                    try:
                        novel.save()
                    except:
                        pass
            else:
                item['src_campaign_id'] = campaign.campaign_source.id
                for url in ['src_url', 'src_latest_chapter_url']:
                    val = item.get(url, "")
                    if val:
                        item[url] = self.full_schema_url(val or "")

                new_data.append(Novel(**item))

        if new_data:
            Novel.objects.bulk_create(new_data, ignore_conflicts=True)

        if 0 < no_update_limit <= no_update_count:
            continue_paging = False

        return continue_paging


class NovelChapterSerializer(serializers.Serializer):
    chapter_name = serializers.CharField()
    chapter_url = serializers.CharField()


class NovelInfoCampaignSchema(serializers.Serializer):
    url = serializers.CharField()
    name = serializers.CharField(required=False)
    thumbnail_image = serializers.CharField(required=False)
    status = serializers.CharField(required=False)
    authors = serializers.ListField(required=False)
    genres = serializers.ListField(required=False)
    descriptions = serializers.CharField(required=False)
    list_chapter = NovelChapterSerializer(many=True, required=False)


class NovelInfoCampaignType(BaseCrawlCampaignType):
    schema_class = NovelInfoCampaignSchema
    name = 'NOVEL_INFO'
    model_class = Novel
    update_by_fields = ['src_url']

    def handle(self, crawled_data, campaign, *args, **kwargs):
        continue_paging = super().handle(crawled_data, campaign, *args, **kwargs)
        for field in self.update_by_fields:
            sleep(0.01)
            crawled_data['src_url'] = crawled_data.pop('url', '').rstrip("/")
            crawled_data['name'] = crawled_data.get('name', '').lower().title()
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

            chapters = {self.full_schema_url(chapter.get("chapter_url")): chapter.get("chapter_name")
                        for chapter in crawled_data.get("list_chapter") or []}

            if chapters:
                exist_chapters = NovelChapter.objects.filter(src_url__in=list(chapters.keys()))
                for ex_chap in exist_chapters:
                    name = chapters.pop(ex_chap.src_url)
                    if ex_chap.name != name:
                        ex_chap.name = name
                        ex_chap.chapter_updated = False
                        ex_chap.save()
                        update = True

                new_chapters = [NovelChapter(novel=novel, name=name, src_url=url, novel_slug=novel.slug)
                                for url, name in chapters.items()]
                if new_chapters:
                    NovelChapter.objects.bulk_create(new_chapters, ignore_conflicts=True)
                    novel.latest_updated_time = datetime.now()
                    novel.update_flat_info()
                    update = True

            status = crawled_data.get("status")
            if status and (not novel.status or status != novel.status.name):
                status, _ = Status.objects.get_or_create(name=status.title().strip())
                novel.status = status
                update = True

            descriptions = crawled_data.get("descriptions")
            if not novel.descriptions and descriptions:
                novel.descriptions = descriptions
                update = True

            if update:
                novel.publish = True
                novel.novel_updated = True
            elif novel.attempt >= 10:
                novel.publish = False
                novel.novel_updated = False
                novel.active = False
            else:
                novel.attempt += 1

            novel.save()

        return continue_paging


class NovelChapterCampaignSchema(serializers.Serializer):
    url = serializers.CharField()
    content_text = serializers.CharField(required=False)
    content_images = serializers.ListField(required=False)


class NovelChapterCampaignType(BaseCrawlCampaignType):
    schema_class = NovelChapterCampaignSchema
    name = 'NOVEL_CHAPTER'
    model_class = NovelChapter
    update_by_fields = ['src_url']

    def handle(self, crawled_data, campaign, *args, **kwargs):
        continue_paging = super().handle(crawled_data, campaign, *args, **kwargs)

        for field in self.update_by_fields:
            sleep(0.01)
            crawled_data['src_url'] = crawled_data.pop('url', '').rstrip("/")
            chapter = self.update_values.get(field, {}).get(crawled_data.get(field))
            if not chapter:
                continue

            updated = False
            content_text = crawled_data.get("content_text")
            if content_text:
                compressed = zlib.compress(content_text.encode())
                chapter.binary_content = compressed
                updated = True

            content_images = crawled_data.get("content_images")
            if content_images:
                chapter.images_content = '\n'.join(content_images)
                # chapter.novel.update_flat_info()
                # chapter.novel.save()
                updated = True

            if updated:
                chapter.chapter_updated = True
                chapter.save()
            elif chapter.attempt >= 10:
                chapter.chapter_updated = False
                chapter.active = False
            else:
                chapter.attempt += 1

        return continue_paging
