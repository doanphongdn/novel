import re
from urllib.parse import urlparse

from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from novel.cache_manager import NovelCache
from novel.models import Novel
from novel.views.base import NovelBaseView


class NovelDetailView(NovelBaseView):
    template_name = "novel/novel.html"

    @staticmethod
    def update_hot_point(request):
        try:
            novel_id = request.POST.get('q[nid]', "")
            if novel_id:
                novel = Novel.objects.filter(pk=novel_id, active=True).first()
                if novel:
                    novel.hot_point += 1
                    novel.save()
                return JsonResponse({"success": True, })
        except Exception as e:
            return JsonResponse({"success": False, "err": e})

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        search = request.POST.get('q', "")
        if len(search) >= 3:
            novels = NovelCache(Novel, **{"name__unaccent__icontains": search.strip()}) \
                         .get_from_cache(get_all=True)[:15]
            if not novels:
                # split to multiple keywords
                unique_sub_keywords = set(re.split(r'\W+', search))
                conditions = {
                    "name__unaccent__iregex": r'(' + '|'.join([k for k in unique_sub_keywords if len(k) > 2]) + ')'
                }
                novels = NovelCache(Novel, **conditions).get_from_cache(get_all=True)[:10]

            res_data = []
            for novel in novels:
                res_data.append({
                    "thumbnail_image": novel.thumbnail_image,
                    "name": novel.name,
                    "url": novel.get_absolute_url(),
                    "nid": novel.id,
                })

            return JsonResponse({"data": res_data})

        return JsonResponse({"data": []})

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        chapter_page = request.GET.get('chap-page') or 1
        slug = kwargs.get('slug')
        if not slug:
            # TODO: define 404 page
            # direct to homepage
            return redirect('home')

        novel = NovelCache(Novel, **{"slug": slug}).get_from_cache()
        if novel:
            referer = urlparse(novel.src_url)
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
            },
            "comment": {
                "novel": novel,
                # Dont change cke_id, it using in base.js
                "cke_novel_id": "cke_novel_id",
            },
            "report_modal": {
                "novel": novel
            }
        }
        domain = response.context_data.get("setting", {}).get("domain", "")
        response.context_data.update({
            'novel_html': self.incl_manager.render_include_html("novel", extra_data=extra_data, request=request),
            'novel': novel,
            "thumbnail_image": domain + novel.stream_thumbnail_image,
        })
        return response
