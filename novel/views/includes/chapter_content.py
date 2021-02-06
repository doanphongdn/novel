import hashlib
import json
import os
from urllib.parse import urlparse

<<<<<<< HEAD
from cms.cache_manager import CacheManager
=======
from django.contrib.sites.shortcuts import get_current_site

from crawl_service import settings as craw_settings, utils
from crawl_service.utils import full_schema_url
>>>>>>> 6f04978... Update alias cdn
from novel import settings
from novel.models import NovelSetting
from novel.views.includes.base import BaseTemplateInclude


class ChapterContentTemplateInclude(BaseTemplateInclude):
    name = "chapter_content"
    template = "novel/includes/chapter_content.html"

    @staticmethod
    def stream_images(chapter):
        # Get novel setting from cache
        novel_setting = CacheManager(NovelSetting).get_from_cache()
        img_ignoring = []
        if novel_setting and novel_setting.img_ignoring:
            img_ignoring = novel_setting.img_ignoring.split(",")

        stream_images = []
<<<<<<< HEAD
        images = chapter.images
        for image in images:
            # Not allow img url contains any sub-string from a list configuration's string
            if len(img_ignoring) and any(sub_str in image for sub_str in img_ignoring):
                continue
=======
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
>>>>>>> 6f04978... Update alias cdn

            referer = urlparse(chapter.src_url)
            referer_url = referer.scheme + "://" + referer.netloc

            if 'blogspot.com' in image:
                referer_url = None

<<<<<<< HEAD
            json_str = json.dumps({
                "origin_url": image,
                "referer": referer_url,
            })
            image_hash = hashlib.md5(json_str.encode()).hexdigest()
            if not settings.redis_image.get(image_hash):
                settings.redis_image.set(image_hash, json_str)
=======
                if cdn_file_url or cdn_friendly_alias_url:
                    novel_slug = utils.str_format_num_alpha_only(chapter.novel.slug)
                    chapter_slug = utils.str_format_num_alpha_only(chapter.slug)
                    file_path = "%s/%s" % (novel_slug, chapter_slug)
                    full_origin_url = full_schema_url(image, referer)
                    _, ext = os.path.splitext(full_origin_url)
                    target_file = "%s/%s/%s%s" % (cdn_file_url.strip('/'), file_path, str(idx), ext or '.jpg')
                    cdn_referer = None
                    if cdn_friendly_alias_url:
                        current_site = get_current_site(chapter)
                        if current_site:
                            target_file = "%s/%s/%s%s" % (cdn_friendly_alias_url.strip('/'), file_path, str(idx), ext)
                            cdn_referer = "http://" + current_site.domain if 'http' not in current_site.domain else current_site.domain

                    if target_file:
                        json_obj.update({'cdn_origin_url': target_file, 'cdn_referer': cdn_referer})
>>>>>>> 6f04978... Update alias cdn

            stream_images.append("/images/%s.jpg" % image_hash)

        return stream_images

    def prepare_include_data(self):
        chapter = self.include_data.get("chapter")
        chapter_prev_url = None
        if chapter.prev_chapter:
            chapter_prev_url = chapter.prev_chapter.get_absolute_url()

        chapter_next_name = None
        chapter_next_url = None
        if chapter.next_chapter:
            chapter_next_url = chapter.next_chapter.get_absolute_url()
            chapter_next_name = chapter.next_chapter.name

        self.include_data.update({
            "chapter_prev_url": chapter_prev_url,
            "chapter_next_url": chapter_next_url,
            "chapter_next_name": chapter_next_name,
            "stream_images": self.stream_images(chapter),
        })
