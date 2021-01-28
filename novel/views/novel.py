from urllib.parse import urlparse

from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse, StreamingHttpResponse, HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from cms.models import TemplateManager
from novel.models import Novel
from novel.views.base import NovelBaseView
from novel.views.chapter import url2yield


class NovelDetailView(NovelBaseView):
    template_name = "novel/novel.html"

    @method_decorator(csrf_protect)
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
            if any(gen for gen in novel.genres.all() if novel and not gen.active):
                return redirect("home")

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
            return redirect('home')

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
            'request_url': request.build_absolute_uri(),
        })

        return response

    def stream_thumbnail_image(self, *args, **kwargs):
        img = kwargs.get('img') or ""
        image_files = img.strip('.jpg').split('_')
        novel = Novel.objects.filter(id=image_files[0]).first()
        if novel:
            referer = urlparse(novel.url)
            referer_url = referer.scheme + "://" + referer.netloc
            origin_url = novel.thumbnail_image.strip()

            if origin_url.strip().startswith('//'):
                origin_url = referer.scheme + ":" + origin_url

            elif origin_url.strip().startswith('/static'):
                referer_url = None
                current_site = get_current_site(self)
                origin_url = ('https' if self.is_secure() else 'http') + "://" + current_site.domain + origin_url

            elif origin_url.strip().startswith('/'):
                origin_url = referer_url.strip('/') + "/" + origin_url

            if 'blogspot.com' in origin_url:
                referer_url = None
            return StreamingHttpResponse(url2yield(origin_url, referer=referer_url),
                                         content_type="image/jpeg")
        return HttpResponse({})
