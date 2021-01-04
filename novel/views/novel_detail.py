from django.core.paginator import Paginator
from django.http import JsonResponse

from novel.models import Novel
from novel.views.base import NovelBaseView
from novel.widgets.chapter_list import ChapterListWidget
from novel.widgets.novel_grid import NovelGridWidget


class NovelDetailView(NovelBaseView):
    template_name = "novel/novel_detail.html"

    def post(self, request, *args, **kwargs):
        search = request.POST.get('q', "")
        if len(search) >= 3:
            novels = Novel.get_available_novel().filter(name__icontains=search)
            res_data = []
            for novel in novels:
                res_data.append({
                    "thumbnail_image": novel.thumbnail_image,
                    "name": novel.name,
                    "latest_chapter_name": novel.chapters and novel.chapters[0].name or "",
                    "url": novel.get_absolute_url(),
                })

            return JsonResponse({"data": res_data})

        return JsonResponse({"data": []})

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        chapter_page = request.GET.get('chapter-page') or 1
        slug = kwargs.get('slug')

        novel = Novel.objects.filter(slug=slug).first()

        chapters = None
        breadcrumb_data = []
        if novel:
            chapters = novel.chapters.all()
            chapters = Paginator(chapters, 30)
            try:
                chapters = chapters.page(chapter_page)
            except:
                pass

            breadcrumb_data = [{
                "name": novel.name,
                "url": novel.get_absolute_url(),
            }]

        list_novel = Novel.get_available_novel().all()

        chapter_widget = ChapterListWidget(chapters=chapters, title="CHAPTERS", fa_icon="fas fa-book")
        novel_grid = NovelGridWidget(novels=list_novel[:6], title="RELATED NOVEL", fa_icon="far fa-calendar-check")

        response.context_data.update({
            'novel': novel,
            'breadcrumb_data': breadcrumb_data,
            'chapter_widget': chapter_widget,
            'same_category': novel_grid,
        })

        return response
