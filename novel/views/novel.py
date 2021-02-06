import logging
import re
from urllib.parse import urlparse

from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from novel.cache_manager import NovelCache
from novel.models import Novel
from novel.views.base import NovelBaseView
from novel.views.chapter import url2yield


logger = logging.getLogger(__name__)


class NovelDetailView(NovelBaseView):
    template_name = "novel/novel.html"

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        search = request.POST.get('q', "")
        if len(search) >= 3:
            novels = Novel.get_available_novel().filter(name__unaccent__icontains=search.strip()).order_by('name')[:15]
            if not novels:
                # split to multiple keywords
                unique_sub_keywords = set(re.split('\W+', search))
                novels = Novel.get_available_novel().filter(
                    name__unaccent__iregex=r'(' + '|'.join([k for k in unique_sub_keywords if len(k) > 2]) + ')'
                ).order_by('name')[:10]
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

        try:
            chapter_page = request.GET.get('chap-page') or 1
            slug = kwargs.get('slug')
            if not slug:
                # TODO: define 404 page
                # direct to homepage
                return redirect('home')

            novel = NovelCache().get_from_cache(slug=slug)
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
                    "chap_page": chapter_page,
                }
            }
            response.context_data.update({
                'include_html': self.incl_manager.render_include_html("novel", extra_data=extra_data),
                'request_url': request.build_absolute_uri(),
                'novel': novel,
            })
        except Exception as e:
            logger.error('[NovelDetailView] get view Error %s', e)
            # TODO: define 404 page
            # direct to homepage
            return redirect('home')

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
