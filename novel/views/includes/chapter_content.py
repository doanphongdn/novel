import hashlib
import json
from urllib.parse import urlparse

from cms.cache_manager import CacheManager
from crawl_service import settings as crawl_settings
from novel import settings
from novel.models import NovelSetting
from novel.utils import sort_images
from novel.views.includes.base import BaseTemplateInclude


class ChapterContentTemplateInclude(BaseTemplateInclude):
    name = "chapter_content"
    template = "novel/includes/chapter_content.html"

    @staticmethod
    def stream_images(chapter, cdn_img_count=0):
        stream_images = []
        if not chapter:
            return stream_images
        try:
            # Get novel setting from cache
            novel_setting = CacheManager(NovelSetting).get_from_cache()
            img_ignoring = []
            if novel_setting and novel_setting.img_ignoring:
                img_ignoring = novel_setting.img_ignoring.split(",")

            images = chapter.images
            for idx, image in enumerate(images):
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

                for ignoring_referer in crawl_settings.IGNORE_REFERER_FOR.split(","):
                    if ignoring_referer in origin_url:
                        referer_url = None
                        break

                json_obj = {
                    "origin_url": origin_url,
                    "referer": referer_url,
                    "chapter": chapter.id,
                }
                if idx == cdn_img_count:
                    json_obj.update({"chapter_updated": chapter.chapter_updated, })
                json_str = json.dumps(json_obj)
                image_hash = hashlib.md5(origin_url.encode()).hexdigest()
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
        novel = self.include_data.get("novel")

        chapter_prev_url = None
        if chapter and chapter.prev_chapter:
            chapter_prev_url = chapter.prev_chapter.get_absolute_url()

        chapter_next_name = None
        chapter_next_url = None
        if chapter and chapter.next_chapter:
            chapter_next_url = chapter.next_chapter.get_absolute_url()
            chapter_next_name = chapter.next_chapter.name

        cdnnovelfile = chapter.cdnnovelfile_set.first() if chapter else None
        cdn_images = None
        cdn_domain = None
        # Sometime CDN unable to download all img, and missing some of them
        # we hav eto fit these position by streaming img url
        missing_img_pos = None
        if cdnnovelfile:
            cdn_images = cdnnovelfile.url.split('\n') if cdnnovelfile.url else None
            if cdn_images:
                cdn_images, missing_img_pos = sort_images(cdn_images)
            if crawl_settings.BACKBLAZE_FRIENDLY_ALIAS_URL:
                cdn_domain = crawl_settings.BACKBLAZE_FRIENDLY_ALIAS_URL
            elif crawl_settings.BACKBLAZE_FRIENDLY_URL:
                cdn_domain = crawl_settings.BACKBLAZE_FRIENDLY_URL
            if not cdn_domain and cdnnovelfile.cdn:
                cdn_domain = cdnnovelfile.cdn.friendly_alias_url or cdnnovelfile.cdn.friendly_url or cdnnovelfile.cdn.s3_url

        chapter_list = []
        if novel and novel.novel_flat:
            chapter_list = novel.novel_flat.chapters.get("list")

        pos_of_stream = 0
        if cdn_images and cdn_domain:
            pos_of_stream = len(cdn_images)
            if missing_img_pos:
                pos_of_stream = missing_img_pos[0]
        stream_images = self.stream_images(chapter, pos_of_stream)

        mix_images = []
        if missing_img_pos:
            # use list(a) or a[:] to copy values only
            mix_images = cdn_images[:]

        for idx in missing_img_pos:
            mix_images.insert(idx, stream_images[idx])

        self.include_data.update({
            "chapter_list": chapter_list,
            "chapter_prev_url": chapter_prev_url,
            "chapter_next_url": chapter_next_url,
            "chapter_next_name": chapter_next_name,
            "mix_images": mix_images,
            "stream_images": stream_images,
            "cdn_images": cdn_images if cdn_images and cdn_domain else [],
            "cdn_domain": cdn_domain.rstrip('/') if cdn_domain else None
        })
