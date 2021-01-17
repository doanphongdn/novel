from django.http import JsonResponse
from django.shortcuts import redirect

from cms.models import TemplateManager
from novel.models import Novel
from novel.views.base import NovelBaseView
from novel.views.includes.__mapping import IncludeMapping


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

        chapter_page = request.GET.get('chap-page') or 1
        slug = kwargs.get('slug')

        novel = Novel.objects.filter(slug=slug).first()

        # chapters = None
        # breadcrumb_data = []
        if novel:
            response.context_data["setting"]["title"] = novel.name
            keywords = [novel.slug.replace('-', ' '), novel.name, novel.name + ' full']
            response.context_data["setting"]["meta_keywords"] += ', ' + ', '.join(keywords)

            chapters = novel.chapters.all()

            breadcrumb_data = [{
                "name": novel.name,
                "url": novel.get_absolute_url(),
            }]
        else:
            # TODO: define 404 page
            # not found the page
            # redirect to home page
            return redirect('/')  # or redirect('name-of-index-url')
        #
        # list_novel = Novel.get_available_novel().all()
        #
        # include_data = {
        #     "novels": list_novel,
        #     "title": "RELATED NOVEL",
        #     "icon": "far fa-calendar-check",
        #     "limit": 6,
        # }
        # related = NovelListTemplateInclude(**include_data)
        #
        # include_data = {
        #     "chapters": chapters,
        #     "title": "CHAPTER LIST",
        #     "icon": "fa fa-list",
        #     "limit": 30,
        #     "page": chapter_page,
        # }
        # chapter_list = ChapterListTemplateInclude(**include_data)
        # breadcrumb = BreadCrumbTemplateInclude(data=breadcrumb_data)

        extra_data = {
            "breadcrumb": {
                "breadcrumb_data": breadcrumb_data,
            },
            "novel_info": {
                "novel": novel,
            },
            "chapter_list": {
                "chap_data": chapters,
                "chap_page": chapter_page,
            }
        }
        tmpl = TemplateManager.objects.filter(page_file='novel').first()
        response.context_data.update({
            'include_html': IncludeMapping.render_include_html(tmpl, extra_data=extra_data),
        })

        return response
