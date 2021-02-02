import hashlib

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
        images = chapter.images
        stream_images = []
        for i in range(len(images)):
            # Not allow img url contains any sub-string from a list configuration's string
            if len(img_ignoring) and any(sub_str in images[i] for sub_str in img_ignoring):
                continue
            stream_images.append("/images/%s_%s_%s.jpg" % (chapter.id, i, hashlib.md5(images[i].encode()).hexdigest()))
        return stream_images

    def __init__(self, include_data, extra_data=None):
        super().__init__(include_data, extra_data)
        chapter = self.include_data.get("chapter")

        self.include_data = {
            "chapter": chapter,
            "stream_images": self.stream_images(chapter),
        }
