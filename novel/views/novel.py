from urllib.parse import urlparse

from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from cms.models import TemplateManager
from novel.models import Novel
from novel.views.base import NovelBaseView


class NovelDetailView(NovelBaseView):
    template_name = "novel/novel.html"

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        search = request.POST.get('q', "")
        if len(search) >= 3:
            novels = Novel.get_available_novel().filter(name__unaccent__icontains=search.strip()).order_by('name')[:15]
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

        if novel:
            referer = urlparse(novel.url)
            if novel.thumbnail_image.strip().startswith('//'):
                referer_url = referer.scheme  # + referer.netloc
            else:
                referer_url = referer.scheme + "://"  # + referer.netloc

            response.context_data["setting"]["title"] = novel.name
            response.context_data['setting']['meta_img'] = referer_url + novel.thumbnail_image
            keywords = [novel.slug.replace('-', ' '), novel.name, novel.name + ' full']
            response.context_data["setting"]["meta_keywords"] += ', ' + ', '.join(keywords)

            chapters = novel.chapters.all()

            breadcrumb_data = [{
                "name": novel.name,
                "url": novel.get_absolute_url(),
            }]
        else:
            return redirect('/')

        extra_data = {
            "breadcrumb": {
                "breadcrumb_data": breadcrumb_data,
            },
            "novel_info": {
                "novel": novel,
            },
            "chapter_list": {
                "novel": novel,
                "chap_data": chapters,
                "chap_page": chapter_page,
            }
        }
        tmpl = TemplateManager.objects.filter(page_file='novel').first()
        response.context_data.update({
            'include_html': self.include_mapping.render_include_html(tmpl, extra_data=extra_data),
        })

        return response
