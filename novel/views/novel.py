from django.core.paginator import Paginator
from django.http import JsonResponse

from novel.models import Novel
from novel.views.base import NovelBaseView
from novel.views.includes.breadcrumb import BreadCrumbTemplateInclude
from novel.views.includes.chapter_list import ChapterListTemplateInclude
from novel.views.includes.novel_info import NovelInfoTemplateInclude
from novel.views.includes.novel_list import NovelListTemplateInclude


class NovelDetailView(NovelBaseView):
    template_name = "novel/novel.html"

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
            response.context_data["setting"]["title"] = novel.name
            keywords = [novel.slug.replace('-', ' '), novel.name, novel.name + ' full']
            response.context_data["setting"]["meta_keywords"] += ', ' + ', '.join(keywords)

            chapters = novel.chapters.all()

            breadcrumb_data = [{
                "name": novel.name,
                "url": novel.get_absolute_url(),
            }]

        list_novel = Novel.get_available_novel().all()

        include_data = {
            "novels": list_novel,
            "title": "RELATED NOVEL",
            "icon": "far fa-calendar-check",
            "limit": 6,
        }
        related = NovelListTemplateInclude(**include_data)

        include_data = {
            "chapters": chapters,
            "title": "CHAPTER LIST",
            "icon": "fa fa-list",
            "limit": 30,
            "page": chapter_page,
        }
        chapter_list = ChapterListTemplateInclude(**include_data)
        breadcrumb = BreadCrumbTemplateInclude(data=breadcrumb_data)
        novel_info = NovelInfoTemplateInclude(novel=novel)

        response.context_data.update({
            'novel_info_html': novel_info.render_html(),
            'breadcrumb_html': breadcrumb.render_html(),
            'chapter_list_html': chapter_list.render_html(),
            'related_html': related.render_html(),
        })

        return response
