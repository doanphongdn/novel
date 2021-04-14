import re
from http import HTTPStatus
from urllib.parse import urlparse

from django.db.models.query import QuerySet
from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _, activate
from django.views.decorators.csrf import csrf_protect

from django_cms import settings
from novel.cache_manager import NovelCache
from novel.form.report import ReportForm
from novel.models import Novel, NovelReport
from novel.views.base import NovelBaseView


class NovelAction(object):
    @staticmethod
    def report_form(request):
        if request.method == 'POST':
            report_form = ReportForm(request.POST)
            if report_form.is_valid():
                user = request.user if not isinstance(request.user, AnonymousUser) else None
                novel_id = request.POST.get('novel_id')
                chapter_id = request.POST.get('chapter_id')
                content = request.POST.get('content')
                NovelReport.objects.create(user=user, novel_id=novel_id, chapter_id=chapter_id, content=content)

                activate(settings.LANGUAGE_CODE)
                return JsonResponse({
                    "status": True, "message": _(
                        'Thank you for sending us errors, we will check and process as soon as possible.')
                },
                    status=HTTPStatus.OK)

        return JsonResponse({"status": False}, status=HTTPStatus.OK)


class NovelDetailView(NovelBaseView):
    template_name = "novel/novel.html"
    ads_group_name = "novel_info"

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
        if len(search) > 2:
            limit = 10
            novels = NovelCache(Novel, limit=limit, **{"name__unaccent__icontains": search.strip(), "active": True}) \
                .get_from_cache(get_all=True)
            if not novels:
                # split to multiple keywords
                unique_sub_keywords = set(re.split(r'\W+', search))
                conditions = {
                    "name__unaccent__iregex": r'(' + '|'.join([k for k in unique_sub_keywords if len(k) > 2]) + ')'
                }
                novels = NovelCache(Novel, limit=limit, **conditions).get_from_cache(get_all=True)

            res_data = []
            # cache get an object Novel
            if isinstance(novels, Novel):
                novels = [novels]
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
            return redirect('home', permanent=True)

        novel = NovelCache(Novel, **{"slug": slug}).get_from_cache()
        if novel:
            if isinstance(novel, QuerySet):
                novel = novel[0]
            referer = urlparse(novel.src_url)
            if novel.thumbnail_image:
                if novel.thumbnail_image.strip().startswith('//'):
                    response.context_data['setting']['meta_img'] = referer.scheme + ":" + novel.thumbnail_image.strip()
                elif novel.thumbnail_image.strip().startswith('http'):
                    response.context_data['setting']['meta_img'] = novel.thumbnail_image.strip()
                else:
                    response.context_data['setting']['meta_img'] = referer.scheme + "://" + novel.thumbnail_image

            response.context_data["setting"]["title"] = novel.name

            # title for social
            # setting = response.context_data.get("setting")
            response.context_data["setting"]["meta_og_title"] = novel.name

            keywords = [novel.slug.replace('-', ' '), novel.name, novel.name + ' full']
            response.context_data["setting"]["meta_keywords"] += ', ' + ', '.join(keywords)

            breadcrumb_data = [{
                "name": novel.name,
                "url": novel.get_absolute_url(),
            }]
        else:
            return redirect('home')

        # novels = NovelCache(Novel, **{"genres__in": novel.genre_all}, limit=12).get_from_cache(
        #     get_all=True).distinct().exclude(id=novel.id).all()
        ads_data = response.context_data.get("ads_data", {})
        extra_data = {
            "breadcrumb": {
                "breadcrumb_data": breadcrumb_data,
            },
            "novel_info": {
                "novel": novel,
                "novel_info_ads": ads_data.get("novel_info_right"),
                "novel_info_after_thumbnail": ads_data.get("novel_info_after_thumbnail"),
            },
            "chapter_list": {
                "novel": novel,
                "chap_page": chapter_page,
                "chapter_list_before_ads": ads_data.get("novel_info_before_chap_list"),
                "chapter_list_after_ads": ads_data.get("novel_info_after_chap_list"),
            },
            "comment": {
                "novel": novel,
                "comment_ads": ads_data.get("novel_info_before_comment"),
                # Dont change cke_id, it using in base.js
                "cke_novel_id": "cke_novel_id",
            },
            "report_modal": {
                "novel": novel
            },
            "novel_list": {
                "filter_by": {"genres__in": novel.genre_all},
                "exclude": {"id": novel.id},
                "distinct": True,
            }
        }
        latest_chap = novel.novel_flat and novel.novel_flat.latest_chapter.get("name") or ""
        domain = response.context_data.get("setting", {}).get("domain", "")
        response.context_data["setting"]["title"] = "%s [%s]" % (response.context_data["setting"]["title"], latest_chap)
        response.context_data.update({
            'novel_html': self.incl_manager.render_include_html("novel", extra_data=extra_data, request=request),
            'novel': novel,
            "thumbnail_image": domain + novel.stream_thumbnail_image,
        })
        return response
