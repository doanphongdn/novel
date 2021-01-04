from django.core.paginator import Paginator
from django.http import JsonResponse

from novel.models import Novel, NovelChapter
from novel.views.base import NovelBaseView
from novel.widgets.chapter_list import ChapterListWidget
from novel.widgets.novel_grid import NovelGridWidget


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

        response.context_data.update({
            'chapter': chapter,
            'breadcrumb_data': breadcrumb_data,
        })

        return response
