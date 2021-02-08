import hashlib
import json
from urllib.parse import urlparse

from cms.cache_manager import CacheManager
from novel import settings
from crawl_service import settings as crawl_settings
from novel.models import NovelSetting
from novel.views.includes.base import BaseTemplateInclude


class ChapterContentTemplateInclude(BaseTemplateInclude):
    name = "chapter_content"
    template = "novel/includes/chapter_content.html"

    @staticmethod
    def stream_images(chapter):
        stream_images = []
        try:
            # Get novel setting from cache
            novel_setting = CacheManager(NovelSetting).get_from_cache()
            img_ignoring = []
            if novel_setting and novel_setting.img_ignoring:
                img_ignoring = novel_setting.img_ignoring.split(",")

            images = chapter.images
            for image in images:
                # Not allow img url contains any sub-string from a list configuration's string
                if len(img_ignoring) and any(sub_str in image for sub_str in img_ignoring):
                    continue

                referer = urlparse(chapter.src_url)
                referer_url = referer.scheme + "://" + referer.netloc

                origin_url = (image or "").strip()

                if origin_url.strip().startswith('//'):
                    origin_url = referer.scheme + ":" + origin_url
                elif origin_url.strip().startswith('/'):
                    origin_url = referer_url.strip('/') + "/" + origin_url
                if 'blogspot.com' in origin_url:
                    referer_url = None

                json_str = json.dumps({
                    "origin_url": origin_url,
                    "referer": referer_url,
                })
                image_hash = hashlib.md5(json_str.encode()).hexdigest()
                if not settings.redis_image.get(image_hash):
                    settings.redis_image.set(image_hash, json_str)

                stream_images.append("/images/%s.jpg" % image_hash)

        except Exception as e:
            print("[stream_images] Error when parse image chapter content %s" % e)
            import traceback
            traceback.print_exc()

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

        cdnnovelfile = chapter.cdnnovelfile_set.first()
        cdn_images = None
        cdn_domain = None
        if cdnnovelfile:
            cdn_images = cdnnovelfile.url.split('\n') if cdnnovelfile.url else None
            if crawl_settings.BACKBLAZE_FRIENDLY_ALIAS_URL:
                cdn_domain = crawl_settings.BACKBLAZE_FRIENDLY_ALIAS_URL
            elif crawl_settings.BACKBLAZE_FRIENDLY_URL:
                cdn_domain = crawl_settings.BACKBLAZE_FRIENDLY_URL
            if not cdn_domain and cdnnovelfile.cdn:
                cdn_domain = cdnnovelfile.cdn.friendly_alias_url or cdnnovelfile.cdn.friendly_url or cdnnovelfile.cdn.s3_url

        self.include_data.update({
            "chapter_prev_url": chapter_prev_url,
            "chapter_next_url": chapter_next_url,
            "chapter_next_name": chapter_next_name,
            "stream_images": self.stream_images(chapter),
            "cdn_images": cdn_images if cdn_images and cdn_domain else [],
            "cdn_domain": cdn_domain if cdn_domain else None
        })
