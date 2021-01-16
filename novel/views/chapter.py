from urllib.parse import urlparse

import requests
from django.http import StreamingHttpResponse, HttpResponse
from django.shortcuts import redirect

from novel.models import Novel, NovelChapter, NovelSetting
from novel.views.base import NovelBaseView
from novel.views.includes.breadcrumb import BreadCrumbTemplateInclude
from novel.views.includes.chapter_content import ChapterContentTemplateInclude
from novel.views.includes.chapter_image import ChapterImageTemplateInclude
from novel.views.includes.novel_info import NovelInfoTemplateInclude


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

        chapter = None
        breadcrumb_data = []
        novel = Novel.objects.filter(slug=slug).first()
        if novel:
            chapter = NovelChapter.objects.filter(slug=chapter_slug, novel=novel).first()
            if chapter:
                response.context_data["setting"]["title"] = novel.name + " " + chapter.name
                keywords = [novel.slug.replace('-', ' '), novel.name, novel.name + ' full',
                            chapter.slug.replace('-', ' '), chapter.name]
                response.context_data["setting"]["meta_keywords"] += ', ' + ', '.join(keywords)

            breadcrumb_data = [
                {
                    "name": novel.name,
                    "url": novel.get_absolute_url(),
                },
                {
                    "name": chapter.name,
                    "url": chapter.get_absolute_url(),
                }
            ]
        else:
            # TODO: define 404 page
            # direct to hompage
            return redirect('/')  # or redirect('name-of-index-url')

        breadcrumb = BreadCrumbTemplateInclude(data=breadcrumb_data)

        chapter_content = ChapterContentTemplateInclude(chapter=chapter)

        response.context_data.update({
            'novel_url': novel.get_absolute_url(),
            'chapter_content_html': chapter_content.render_html() if chapter_content else "",
            'breadcrumb_html': breadcrumb.render_html(),
        })

        return response

    def stream_image(self, *args, **kwargs):
        img = kwargs.get('img') or ""
        image_files = img.strip('.jpg').split('_')
        chapter = NovelChapter.objects.filter(id=image_files[0]).first()
        if chapter:
            referer = urlparse(chapter.url)
            referer_url = referer.scheme + "://" + referer.netloc
            origin_url = chapter.images[int(image_files[1])] or ""

            if origin_url.strip().startswith('//'):
                origin_url = referer.scheme + ":" + origin_url

            elif origin_url.strip().startswith('/'):
                origin_url = referer_url.strip('/') + "/" + origin_url

            return StreamingHttpResponse(url2yield(origin_url, referer=referer),
                                         content_type="image/jpeg")
        return HttpResponse({})
