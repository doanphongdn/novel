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

            referer = urlparse(chapter.src_url)
            referer_url = referer.scheme + "://" + referer.netloc

            if 'blogspot.com' in image:
                referer_url = None

            json_str = json.dumps({
                "origin_url": image,
                "referer": referer_url,
            })
            image_hash = hashlib.md5(json_str.encode()).hexdigest()
            if not settings.redis_image.get(image_hash):
                settings.redis_image.set(image_hash, json_str)

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
