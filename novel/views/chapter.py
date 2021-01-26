from urllib.parse import urlparse

import requests
from django.db import transaction
from django.http import StreamingHttpResponse, HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from cms.models import TemplateManager
from novel.models import Novel, NovelChapter
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

    @method_decorator(cache_page(60 * 5), name='cache_chapter')
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        slug = kwargs.get('slug')
        chapter_slug = kwargs.get('chapter_slug')

        novel = Novel.objects.filter(slug=slug).first()
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
                    request.session.set_expiry(3600)

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

        tmpl = TemplateManager.objects.filter(page_file='chapter').first()
        include_html = self.include_mapping.render_include_html(tmpl, extra_data=extra_data)

        response.context_data.update({
            'novel_url': novel.get_absolute_url(),
            'include_html': include_html,
        })

        return response

    def stream_image(self, *args, **kwargs):
        img = kwargs.get('img') or ""
        image_files = img.strip('.jpg').split('_')
        chapter = NovelChapter.objects.filter(id=image_files[0]).first()
        if chapter:
            referer = urlparse(chapter.url)
            referer_url = referer.scheme + "://" + referer.netloc
            origin_url = (chapter.images[int(image_files[1])] or "").strip()

            if origin_url.strip().startswith('//'):
                origin_url = referer.scheme + ":" + origin_url

            elif origin_url.strip().startswith('/'):
                origin_url = referer_url.strip('/') + "/" + origin_url
            if 'blogspot.com' in origin_url:
                referer_url = None
            return StreamingHttpResponse(url2yield(origin_url, referer=referer_url),
                                         content_type="image/jpeg")
        return HttpResponse({})
