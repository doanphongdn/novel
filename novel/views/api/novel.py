import os
import zlib
from datetime import datetime
from functools import reduce
from http import HTTPStatus
from operator import or_
from time import sleep
from urllib.parse import urlparse

from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView

from django_cms import settings
from django_cms.utils.helpers import full_schema_url
from novel import utils
from novel.utils import get_first_number_pattern
from novel.views.api.schema import NovelChapterCampaignSchema, NovelInfoCampaignSchema, NovelListCampaignSchema
from novel.models import Novel, NovelChapter, Author, Genre, Status


class BaseAPIView(APIView):
    api_limit = 1000
    temp_chapters = {}
    temp_novels = {}
    schema_class = None

    def handle_temp_data(self, temp_data, key, value):
        if key not in temp_data:
            if len(temp_data) == self.api_limit:
                temp_data.pop(next(iter(temp_data)))

            temp_data[key] = value

    @classmethod
    def validate_data(cls, schema, crawled_data):
        schema = schema(data=crawled_data)
        schema.is_valid()
        errors = schema.errors
        if errors:
            return False, dict(errors)

        return True, "Data is valid"

    @classmethod
    def parse_response(cls, is_success, continue_paging=True, log_enable=False, message=None, extra_data=None, ):
        if not extra_data:
            extra_data = {}

        if is_success:
            return Response({
                "status": "SUCCESS",
                "message": message or "OK",
                "log_enable": False,
                "continue_paging": continue_paging,
                "extra": extra_data
            }, HTTPStatus.OK)
        else:
            return Response({
                "status": "FAILED",
                "message": message,
                "log_enable": log_enable,
                "continue_paging": False,
                "extra": extra_data
            }, HTTPStatus.BAD_REQUEST)


class NovelAPIView(BaseAPIView):
    def get(self, request, *args, **kwargs):
        src_campaign_code = kwargs.get("src_campaign_code")
        state = request.query_params.get("state")
        if not src_campaign_code or state != "noupdated":
            return Response({}, status=200)

        try:
            limit = int(request.query_params.get("limit"))
        except:
            limit = self.api_limit

        novel_list = Novel.objects.filter(novel_updated=False,
                                          src_campaign=src_campaign_code, active=True).all()[0:limit]
        novel_urls = []
        for novel in novel_list:
            self.handle_temp_data(self.temp_novels, novel.src_url, novel)
            novel_urls.append(novel.src_url)

        return Response(novel_urls, status=200)

    def post(self, request, *args, **kwargs):
        crawled_data = request.data
        is_valid, errors = self.validate_data(NovelListCampaignSchema, crawled_data)
        if not is_valid:
            return self.parse_response(is_success=True, message="Schema invalid", extra_data=errors)

        try:
            no_update_limit = int(request.query_params.get("noupdate_limited"))
        except:
            no_update_limit = 0

        new_data = []
        no_update_count = 0

        values = crawled_data.get('novel_block', [])
        for item in values:
            sleep(0.01)

            src_url = item.pop('url', '').rstrip("/")
            src_latest_chapter_url = item.pop('latest_chapter_url', '').rstrip("/")
            url_parse = urlparse(src_url)
            referer_url = "%s://%s" % (url_parse.scheme, url_parse.netloc)

            # Override src_url for each novel from url crawled
            item['src_url'] = full_schema_url(src_url, referer_url)
            item['src_campaign'] = crawled_data.get('src_campaign', '')
            item['name'] = item.get('name', '').lower().title()
            item['src_latest_chapter_url'] = full_schema_url(src_latest_chapter_url, referer_url)

            conditions = []
            for field in ["src_url", "name"]:
                item_value = item.get(field)
                conditions.append(Q(**{field + "__in": item_value if isinstance(item_value, list) else [item_value]}))

            novel = Novel.objects.filter(reduce(or_, set(conditions))) \
                .prefetch_related('novel_flat').first() if conditions else None

            if novel:
                update = False
                src_latest_chap_url = full_schema_url(item.get('src_latest_chapter_url') or "", referer_url)
                if src_latest_chap_url:
                    db_src_url = novel.novel_flat and novel.novel_flat.latest_chapter.get("source_url") or None
                    need_updated = src_latest_chap_url not in (novel.src_latest_chapter_url, db_src_url)
                    if need_updated and novel.novel_updated:
                        novel.src_latest_chapter_url = src_latest_chap_url
                        novel.novel_updated = False
                        update = True

                    no_update_count += int(not need_updated)
                if item.get('src_url') and novel.src_url != item['src_url']:
                    novel.src_url = item['src_url']
                    update = True
                if item.get("name") and novel.name.lower() != item["name"].lower():
                    novel.name = item["name"]
                    update = True

                if update:
                    # bypass duplicate name
                    try:
                        novel.save()
                    except Exception as e:
                        print("[NovelAPIView post] Error %s " % e)
                        pass
            else:
                new_data.append(Novel(**item))

        if new_data:
            Novel.objects.bulk_create(new_data, ignore_conflicts=True)

        if 0 < no_update_limit <= no_update_count:
            return self.parse_response(is_success=True, continue_paging=False, message="No update limited")

        return self.parse_response(is_success=True)

    def patch(self, request, *args, **kwargs):
        crawled_data = request.data
        src_url = crawled_data.get('src_url', '').rstrip("/")
        url_parse = urlparse(src_url)
        referer_url = "%s://%s" % (url_parse.scheme, url_parse.netloc)

        crawled_data['name'] = crawled_data.get('name', '').lower().title()

        novel = self.temp_novels.get(src_url) or Novel.objects.filter(src_url=src_url).first()
        if not novel:
            return self.parse_response(is_success=True, continue_paging=False, log_enable=True,
                                       message="No novel found")

        is_valid, errors = self.validate_data(NovelInfoCampaignSchema, crawled_data)
        if not is_valid:
            novel.crawl_errors = "Novel schema invalid"
            novel.active = False
            novel.save()
            return self.parse_response(is_success=False, continue_paging=False, message="Novel schema invalid",
                                       extra_data=errors)

        update = False
        thumbnail_image = crawled_data.get('thumbnail_image')
        if not novel.thumbnail_image and thumbnail_image:
            thumbnail_image = full_schema_url(thumbnail_image, src_url)
            local_image = utils.download_image(thumbnail_image, novel.slug, referer=referer_url)

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

        chapters = {full_schema_url(chapter.get("chapter_url"), referer_url): chapter.get("chapter_name")
                    for chapter in crawled_data.get("list_chapter") or []}

        if chapters:
            exist_chapters = NovelChapter.objects.filter(src_url__in=list(chapters.keys()))
            for ex_chap in exist_chapters:
                name = chapters.pop(ex_chap.src_url)
                if name and ex_chap.name != name:
                    ex_chap.name = name.title()
                    ex_chap.chapter_updated = False
                    ex_chap.save()
                    update = True

            chapter_name = name.title()
            chapter_name_index = get_first_number_pattern(chapter_name.name,
                                                          os.environ.get('LANGUAGE_CHAPTER_NAME', 'Chapter'))
            if 'en' not in settings.LANGUAGE_CODE and chapter_name.startswith('Chapter'):
                chapter_name = chapter_name.replace('Chapter', os.environ.get('LANGUAGE_CHAPTER_NAME', 'Chương'))

            new_chapters = [NovelChapter(novel=novel, name=chapter_name, name_index=chapter_name_index, src_url=url,
                                         novel_slug=novel.slug)
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

        elif novel.attempt >= int(os.environ.get('CRAWL_ATTEMPT', 5)):
            novel.active = False
            novel.publish = False
            novel.novel_updated = False

        else:
            novel.attempt += 1

        novel.save()

        return self.parse_response(is_success=True)


class ChapterAPIView(BaseAPIView):
    def get(self, request, *args, **kwargs):
        src_campaign_code = kwargs.get("src_campaign_code")
        state = request.query_params.get("state")
        if not src_campaign_code or state != "noupdated":
            return Response({}, status=200)

        try:
            limit = int(request.query_params.get("limit"))
        except:
            limit = self.api_limit

        chapter_list = NovelChapter.objects.filter(novel__src_campaign=src_campaign_code, chapter_updated=False,
                                                   active=True).all()[0:limit]
        chapter_urls = []
        for chapter in chapter_list:
            chapter_urls.append(chapter.src_url)
            self.handle_temp_data(self.temp_chapters, chapter.src_url, chapter)

        return Response(chapter_urls, status=200)

    def patch(self, request, *args, **kwargs):
        crawled_data = request.data
        src_url = crawled_data.get('src_url', '').rstrip("/")
        url_parse = urlparse(src_url)
        referer_url = "%s://%s" % (url_parse.scheme, url_parse.netloc)

        chapter = self.temp_chapters.get(src_url) or NovelChapter.objects.filter(src_url=src_url).first()
        if not chapter:
            # Continue update
            return self.parse_response(is_success=True, continue_paging=False, log_enable=True,
                                       message="No chapter found")

        is_valid, errors = self.validate_data(NovelChapterCampaignSchema, crawled_data)
        if not is_valid:
            chapter.crawl_errors = "Chapter schema invalid"
            chapter.active = False
            chapter.save()
            return self.parse_response(is_success=False, continue_paging=False, log_enable=True,
                                       message="Chapter schema invalid",
                                       extra_data=errors)

        content_text = crawled_data.get("content_text")
        content_images = [full_schema_url(url, referer_url) for url in crawled_data.get("content_images") or []]
        if content_text:
            compressed = zlib.compress(content_text.encode())
            chapter.binary_content = compressed
            updated = True
        elif content_images:
            chapter.images_content = '\n'.join(content_images)
            # chapter.novel.update_flat_info()
            # chapter.novel.save()
            updated = True
        else:
            chapter.crawl_errors = "No content to update, deactived chapter"
            chapter.active = False
            chapter.save()
            return self.parse_response(is_success=False, continue_paging=False, log_enable=True,
                                       message="No content to update, deactived chapter",
                                       extra_data=errors)

        if updated:
            chapter.chapter_updated = True
            chapter.save()

        return self.parse_response(is_success=True)
