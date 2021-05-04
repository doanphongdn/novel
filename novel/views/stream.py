import json
import logging

import requests
from django.http import HttpResponse, StreamingHttpResponse

from django_cms import settings as crawl_settings
from novel import settings, utils
from novel.models import CrawlNovelRetry, NovelChapter

logger = logging.getLogger(__name__)


def url2yield(url, chunksize=1024, referer=None):
    s = requests.Session()
    if referer:
        s.headers.update({
            "Referer": referer
        })
    # Note: here i enabled the streaming
    response = s.get(url, stream=True)

    chunk = True
    if response.status_code != 200:
        logger.warning("[url2yield][Status = %s] Unable to get image for %s with referer %s",
                       response.status_code, url, referer)
        yield {"status": response.status_code}
        chunk = False

    restrict_config = crawl_settings.IGNORE_CLOUDFLARE_RESTRICT
    if restrict_config and restrict_config in response.url:
        yield {"cloudflare_restricted": "true"}
        chunk = False

    while chunk:
        chunk = response.raw.read(chunksize)

        if not chunk:
            break

        yield chunk


def stream_image(request, *args, **kwargs):
    try:
        img_hash = (kwargs.get('img') or "").strip('.jpg')
        json_str = settings.redis_image.get(img_hash)
        if json_str:
            json_str = json.loads(json_str)

            origin_url = json_str.get("origin_url", "")
            referer_url = json_str.get("referer")
            chapter_id = json_str.get("chapter")
            chapter_updated = json_str.get("chapter_updated")
            is_stream_failed = False
            try:
                response = StreamingHttpResponse(streaming_content=url2yield(origin_url, referer=referer_url),
                                                 content_type="image/jpeg")
                stream_content = list(response.streaming_content)
            except Exception as ex:
                if chapter_id and chapter_updated:
                    chapter = NovelChapter.objects.get(pk=chapter_id)
                    if chapter and chapter.chapter_updated:
                        chapter.chapter_updated = False
                        chapter.save()
                        CrawlNovelRetry.create_crawl_retry(chapter)
                print("[stream_image] Error when parse image %s : %s <chapter %s - updated %s>"
                      % (img_hash, ex, chapter_id, chapter_updated))
                import traceback
                traceback.print_exc()
                return HttpResponse({})

            for item in stream_content:
                json_obj = utils.is_json(item)
                if json_obj and json_obj.get('cloudflare_restricted'):
                    is_stream_failed = True
                    break
                elif json_obj and json_obj.get('status') != 200:
                    # failed to stream from CDN
                    is_stream_failed = True
                    break
                if isinstance(item, (bytes, bytearray)):
                    is_stream_failed = False
                    break

            if response.status_code == 200 and not is_stream_failed:
                response.streaming_content = stream_content
                return response
            else:
                # failed to stream from CDN
                is_stream_failed = True

            if is_stream_failed:
                if chapter_id and chapter_updated:
                    chapter = NovelChapter.objects.get(pk=chapter_id)
                    if chapter and chapter.chapter_updated:
                        chapter.chapter_updated = False
                        chapter.save()
                        CrawlNovelRetry.create_crawl_retry(chapter)

                print("[stream_image] Error when stream image %s : %s <chapter %s - updated %s>"
                      % (img_hash, origin_url, chapter_id, chapter_updated))
                return HttpResponse({})

    except Exception as e:
        print("[stream_image] Error when parse image %s : %s" % (img_hash, e))
        import traceback
        traceback.print_exc()
    return HttpResponse({})
