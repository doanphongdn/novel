import hashlib
import json
from urllib.parse import urlparse

from cms.cache_manager import CacheManager
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
        images = chapter.images
        for image in images:
            # Not allow img url contains any sub-string from a list configuration's string
            if len(img_ignoring) and any(sub_str in image for sub_str in img_ignoring):
                continue

            referer = urlparse(chapter.url)
            referer_url = referer.scheme + "://" + referer.netloc
            origin_url = (image or "").strip()

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

        return stream_images

    def __init__(self, include_data, extra_data=None):
        super().__init__(include_data, extra_data)
        chapter = self.include_data.get("chapter")
        novel = self.include_data.get("novel")

        self.include_data = {
            "chapter": chapter,
            "novel": novel,
            "stream_images": self.stream_images(chapter),
        }
