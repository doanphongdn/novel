from urllib.parse import urlparse

from django.db import transaction
from django.shortcuts import redirect

from novel.cache_manager import NovelCache
from novel.models import NovelChapter, Novel
from novel.views.base import NovelBaseView


class ChapterView(NovelBaseView):
    template_name = "novel/chapter.html"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        slug = kwargs.get('slug')
        chapter_slug = kwargs.get('chapter_slug')
        breadcrumb_data = []

        novel = NovelCache(Novel, **{"slug": slug}).get_from_cache()
        if novel:
            # TODO: not yet apply cache
            chapter = NovelChapter.objects.filter(slug=chapter_slug, novel=novel).first()
            if chapter:
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

                referer = urlparse(chapter.src_url)
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
        else:
            # TODO: define 404 page
            # direct to homepage
            return redirect('/')  # or redirect('name-of-index-url')

        extra_data = {
            "breadcrumb": {
                "breadcrumb_data": breadcrumb_data,
            },
            "chapter_content": {
                "chapter": chapter,
                "novel": novel
            }
        }

        include_html = self.incl_manager.render_include_html('chapter', extra_data=extra_data)
        response.context_data.update({
            'novel_url': novel.get_absolute_url(),
            'include_html': include_html,
            'request_url': request.build_absolute_uri(),
        })

        return response
<<<<<<< HEAD
=======

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
                    if response.status_code == 200:
                        return response
                    else:
                        # failed to stream from CDN
                        cdn_origin_url = None
                # Stream origin image if not found from CDN
                if not cdn_origin_url:
                    return StreamingHttpResponse(url2yield(origin_url, referer=referer_url), content_type="image/jpeg")

            except Exception as e:
                print("[stream_image] Error when parse image %s : %s" % (img_hash, e))
                import traceback
                traceback.print_exc()
                return HttpResponse({})

        return HttpResponse({})
>>>>>>> 6f04978... Update alias cdn
