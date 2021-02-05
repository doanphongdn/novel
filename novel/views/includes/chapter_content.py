import hashlib
import json
import os
from urllib.parse import urlparse

from django.contrib.sites.shortcuts import get_current_site

from crawl_service import settings as craw_settings
from crawl_service.utils import full_schema_url
from novel import settings
from novel.cache_manager import NovelSettingCache
from novel.views.includes.base import BaseTemplateInclude


class ChapterContentTemplateInclude(BaseTemplateInclude):
    name = "chapter_content"
    template = "novel/includes/chapter_content.html"

    @staticmethod
    def stream_images(chapter):
        # Get novel setting from cache
        novel_setting = NovelSettingCache().get_from_cache()
        img_ignoring = []
        if novel_setting and novel_setting.img_ignoring:
            img_ignoring = novel_setting.img_ignoring.split(",")

        stream_images = []
        try:
            ignore_referer_for = craw_settings.IGNORE_REFERER_FOR.split(',')
            cdn_file_url = craw_settings.BACKBLAZE_FRIENDLY_URL
            cdn_friendly_alias_url = craw_settings.BACKBLAZE_FRIENDLY_ALIAS_URL
            if not cdn_file_url:
                cdn_file_url = craw_settings.BACKBLAZE_S3_URL
            # TODO: if BACKBLAZE_FRIENDLY_URL is not set in the .evn file, we should query it from cdn_server
            # and set it into cdn_friendly_url here. Remember cache it as well
            images = chapter.images
            for idx, image in enumerate(images):
                # Not allow img url contains any sub-string from a list configuration's string
                if len(img_ignoring) and any(sub_str in image for sub_str in img_ignoring):
                    continue

                referer = urlparse(chapter.url)
                referer_url = referer.scheme + "://" + referer.netloc
                origin_url = (image or "").strip()

                if origin_url.strip().startswith('//'):
                    origin_url = referer.scheme + ":" + origin_url
                elif origin_url.strip().startswith('/'):
                    origin_url = referer_url.strip('/') + "/" + origin_url

                if len(ignore_referer_for):
                    for ig_referer in ignore_referer_for:
                        # if 'blogspot.com' in origin_url:
                        if ig_referer in origin_url:
                            referer_url = None
                            break

                json_obj = {
                    "origin_url": origin_url,
                    "referer": referer_url,
                }

                if cdn_file_url or cdn_friendly_alias_url:
                    file_path = "%s/%s" % (chapter.novel.slug, chapter.slug)
                    full_origin_url = full_schema_url(image, referer)
                    _, ext = os.path.splitext(full_origin_url)
                    target_file = "%s/%s/%s%s" % (cdn_file_url.strip('/'), file_path, str(idx), ext)
                    cdn_referer = None
                    if cdn_friendly_alias_url:
                        current_site = get_current_site(chapter)
                        if current_site:
                            target_file = "%s/%s/%s%s" % (cdn_friendly_alias_url.strip('/'), file_path, str(idx), ext)
                            cdn_referer = "http://" + current_site.domain if 'http' not in current_site.domain else current_site.domain

                    if target_file:
                        json_obj.update({'cdn_origin_url': target_file, 'cdn_referer': cdn_referer})

                json_str = json.dumps(json_obj)

                image_hash = hashlib.md5(json_str.encode()).hexdigest()
                if not settings.redis_image.get(image_hash):
                    settings.redis_image.set(image_hash, json_str)

                stream_images.append("/images/%s.jpg" % image_hash)
        except Exception as e:
            print("[stream_images] Error when parse image chapter content %s" % e)
            import traceback
            traceback.print_exc()

        return stream_images

    def __init__(self, include_data, extra_data=None):
        super().__init__(include_data, extra_data)
        chapter = self.include_data.get("chapter")

        self.include_data = {
            "chapter": chapter,
            "stream_images": self.stream_images(chapter),
        }
