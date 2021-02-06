import json
from urllib.parse import urlparse

import requests
from django.db import transaction
from django.http import StreamingHttpResponse, HttpResponse
from django.shortcuts import redirect

from novel import settings
from novel.cache_manager import NovelCache
from novel.models import NovelChapter
from novel.views.base import NovelBaseView


def url2yield(url, chunksize=1024, referer=None):
    s = requests.Session()
    if referer:
        s.headers.update({
            "Referer": referer
        })
    # Note: here i enabled the streaming
    response = s.get(url, stream=True)

    chunk = True
    while chunk:
        chunk = response.raw.read(chunksize)

        if not chunk:
            break

        yield chunk


class ChapterView(NovelBaseView):
    template_name = "novel/chapter.html"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        slug = kwargs.get('slug')
        chapter_slug = kwargs.get('chapter_slug')

        novel = NovelCache().get_from_cache(slug=slug)
        if novel:
            chapter = NovelChapter.objects.filter(slug=chapter_slug, novel=novel).first()
            if chapter:
                referer = urlparse(chapter.url)
                if novel.thumbnail_image.strip().startswith('//'):
                    referer_url = referer.scheme
                else:
                    referer_url = referer.scheme + "://"  # + referer.netloc

                response.context_data["setting"]["title"] = novel.name + " " + chapter.name
                response.context_data['setting']['meta_img'] = referer_url + novel.thumbnail_image
                keywords = [novel.slug.replace('-', ' '), novel.name, novel.name + ' full',
                            chapter.slug.replace('-', ' '), chapter.name]
                response.context_data["setting"]["meta_keywords"] += ', ' + ', '.join(keywords)

                # hard code to ionore index img google bot
                response.context_data["setting"]["no_image_index"] = True

                # Update view count
                chapter_id = chapter.id
                chapters_viewed = request.session.get("chapters_viewed") or []
                if chapter_id not in chapters_viewed:
                    with transaction.atomic():
                        chapter.view_total += 1
                        chapter.save()

                        novel.view_total += 1
                        novel.view_daily += 1
                        novel.view_monthly += 1
                        novel.save()

                        chapters_viewed.append(chapter_id)

                    request.session["chapters_viewed"] = chapters_viewed
                    # request.session.set_expiry(3600)

            breadcrumb_data = [
                {
                    "name": novel.name,
                    "url": novel.get_absolute_url(),
                },
                {
                    "name": chapter.name if chapter else '',
                    "url": chapter.get_absolute_url() if chapter else '',
                }
            ]
        else:
            # TODO: define 404 page
            # direct to homepage
            return redirect('/')  # or redirect('name-of-index-url')

        extra_data = {
            "breadcrumb": {
                "breadcrumb_data": breadcrumb_data,
            },
            "chapter_content": {
                "chapter": chapter
            }
        }

        include_html = self.incl_manager.render_include_html('chapter', extra_data=extra_data)
        response.context_data.update({
            'novel_url': novel.get_absolute_url(),
            'include_html': include_html,
            'request_url': request.build_absolute_uri(),
        })

        return response

    def stream_image(self, *args, **kwargs):
        img_hash = (kwargs.get('img') or "").strip('.jpg')
        json_str = settings.redis_image.get(img_hash)
        if json_str:
            try:
                json_str = json.loads(json_str)

                referer_url = json_str.get("referer")
                cdn_referer = json_str.get("cdn_referer", None)
                cdn_origin_url = json_str.get("cdn_origin_url", "")
                origin_url = json_str.get("origin_url", "")
                if cdn_origin_url:
                    response = StreamingHttpResponse(url2yield(cdn_origin_url, referer=cdn_referer),
                                                     content_type="image/jpeg")
                    try:
                        value = response.getvalue()
                        if response and response.status_code == 200:
                            result = json.loads(value)
                            if result and result.get('status') != 200:
                                # failed to stream from CDN
                                cdn_origin_url = None
                            else:
                                return response
                        else:
                            # failed to stream from CDN
                            cdn_origin_url = None
                    except UnicodeDecodeError as ex:
                        print("[stream_image] Error when stream cdn image %s : %s" % (img_hash, ex))
                        return StreamingHttpResponse(url2yield(origin_url, referer=referer_url),
                                                     content_type="image/jpeg")

                # Stream origin image if not found from CDN
                if not cdn_origin_url:
                    return StreamingHttpResponse(url2yield(origin_url, referer=referer_url), content_type="image/jpeg")

            except Exception as e:
                print("[stream_image] Error when parse image %s : %s" % (img_hash, e))
                import traceback
                traceback.print_exc()
                return HttpResponse({})

        return HttpResponse({})
