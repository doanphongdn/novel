import hashlib
import json
from urllib.parse import urlparse

from django_cms.utils.cache_manager import CacheBalanceRequest, CacheManager
from django_cms import settings as crawl_settings
from novel import settings
from novel.models import NovelSetting
from novel.utils import sort_images
from novel.views.includes.base import BaseTemplateInclude


class ChapterContentTemplateInclude(BaseTemplateInclude):
    name = "chapter_content"
    template = "novel/includes/chapter_content.html"

    @staticmethod
    def stream_images(chapter, cdn_images):
        stream_images = []
        if not chapter:
            return stream_images
        try:
            # Get novel setting from cache
            novel_setting = CacheManager(NovelSetting).get_from_cache()
            img_ignoring = []
            if novel_setting and novel_setting.img_ignoring:
                img_ignoring = novel_setting.img_ignoring.split(",")

            stream_domain = ChapterContentTemplateInclude.get_stream_domain()

            # Some time an outdated chapter will cannot streaming the old images,
            # we have to mark the chapter to 'updated' as false to prepare crawling again
            allow_retry_crawl = True

            images = chapter.images
            for idx, image in enumerate(images):
                # Not allow img url contains any sub-string from a list configuration's string
                if len(img_ignoring) and any(sub_str in image for sub_str in img_ignoring):
                    continue

                referer = urlparse(chapter.src_url)
                referer_url = referer.scheme + "://" + referer.netloc

                origin_url = (image or "").strip()

                if crawl_settings.YOUTUBE_EMBED_DOMAIN in origin_url:
                    stream_images.append(origin_url)
                    continue

                if "<video " in origin_url:
                    stream_images.append(origin_url)
                    continue

                if origin_url.strip().startswith('//'):
                    origin_url = referer.scheme + ":" + origin_url
                elif origin_url.strip().startswith('/'):
                    origin_url = referer_url.strip('/') + "/" + origin_url

                for ignoring_referer in crawl_settings.IGNORE_REFERER_FOR.split(","):
                    if ignoring_referer and ignoring_referer in origin_url:
                        referer_url = None
                        break

                image_hash = hashlib.md5(origin_url.encode()).hexdigest()
                if cdn_images and cdn_images.get(idx):
                    stream_images.append(cdn_images.get(idx))
                    # next to image
                    continue

                json_obj = {
                    "origin_url": origin_url,
                    "referer": referer_url,
                    "chapter": chapter.id,
                }
                if allow_retry_crawl:
                    json_obj.update({"chapter_updated": chapter.chapter_updated, })
                    allow_retry_crawl = False

                json_str = json.dumps(json_obj)

                if not settings.redis_image.get(image_hash):
                    settings.redis_image.set(image_hash, json_str)

                stream_images.append("%s/images/%s/%s/%s.jpg" %
                                     (stream_domain, chapter.novel_slug, chapter.slug, image_hash))

        except Exception as e:
            print("[stream_images] Error when parse image chapter content %s" % e)
            import traceback
            traceback.print_exc()

        return stream_images

    @staticmethod
    def get_stream_domain():
        stream_domains = settings.STREAM_IMAGE_DOMAIN
        if not stream_domains:
            return stream_domains
        domains = []
        stream_domains = stream_domains.split(',')
        for stream_domain in stream_domains:
            domain_lst = stream_domain.split('::')
            domain = {
                'name': domain_lst[0],
            }
            if len(domain_lst) > 1:
                domain['routing_rate'] = domain_lst[1]
            domains.append(domain)
        domain_route = CacheBalanceRequest(domains=domains).get_from_cache()
        return domain_route or ''

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
        # Sometime CDN unable to upload all img, and missing some of them
        # we have to fit these positions by streaming img url
        if cdnnovelfile:
            cdn_domain = crawl_settings.BACKBLAZE_FRIENDLY_ALIAS_URL or crawl_settings.BACKBLAZE_FRIENDLY_URL
            if not cdn_domain and cdnnovelfile.cdn:
                cdn_domain = cdnnovelfile.cdn.friendly_alias_url or cdnnovelfile.cdn.friendly_url or cdnnovelfile.cdn.s3_url
            cdn_images = cdnnovelfile.url.split('\n') if cdnnovelfile.url else None
            if cdn_domain and cdn_images:
                cdn_domain = cdn_domain.rstrip("/") + "/"
                cdn_images = sort_images(cdn_images, cdn_domain)
            else:
                cdn_images = None

        chapter_list = []
        if novel and novel.novel_flat:
            chapter_list = novel.novel_flat.chapters.get("list")

        stream_images = self.stream_images(chapter, cdn_images)

        self.include_data.update({
            "chapter_list": chapter_list,
            "chapter_prev_url": chapter_prev_url,
            "chapter_next_url": chapter_next_url,
            "chapter_next_name": chapter_next_name,
            "stream_images": stream_images,
        })
