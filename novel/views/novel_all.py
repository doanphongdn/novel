from django_cms.utils.cache_manager import CacheManager
from django_cms.models import PageTemplate, Link
from django_cms import settings
from django_cms.utils.include_mapping import IncludeManager
from novel.models import Genre, Status
from novel.views.base import NovelBaseView


class NovelAllView(NovelBaseView):
    template_name = "novel/novel_all.html"
    ads_group_name = "novel_all"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        status = request.GET.get("status", 0)
        genre = kwargs.get('genre')
        novel_type = kwargs.get('novel_type')
        default_config = genre or novel_type

        page_template = IncludeManager.get_page_template('novel_all')
        extra_data = {
            "novel_list": {
                "page": request.GET.get('page') or 1,
                "view_type": request.GET.get('view') or 'grid',
            }
        }

        if genre:
            genre_pre_title = page_template.params.get("genre_pre_title") or ""
            genre_cache = CacheManager(Genre, **{"slug": genre}).get_from_cache(get_all=True)
            genre_obj = genre_cache[0] if genre_cache else None
            title = genre_pre_title + " - " + genre_obj.name if genre_obj else settings.NOVEL_GENRE_URL.upper()
            extra_data['novel_list'].update({
                "filter_by": {"genres__slug": genre},
                "title": title,
                "icon": "fa fa-cubes",
            })
            response.context_data["setting"]["title"] = \
                (genre_pre_title.title() + " " + genre_obj.name if genre_obj else "") \
                + " - " + self.base_setting.get("domain")

        status_groups = page_template.params.get("filter_status_groups") or {}
        link_objs = CacheManager(Link, **{"type": 'novel_filters'}).get_from_cache(get_all=True)
        status_ids = status_groups.get(str(status), {}).get("status_group", [])

        if status_ids:
            extra_data['novel_list'].update({
                "filter_by": {'status_id__in': status_ids},
            })

        ads_data = response.context_data.get("ads_data", {})
        extra_data['novel_list'].update({
             "novel_all_top_ads": ads_data.get("novel_all_top"),
             "novel_all_end_ads": ads_data.get("novel_all_end"),
        })

        response.context_data.update({
            'current_status': status,
            'current_path': request.path,
            'status_groups': status_groups,
            'links': link_objs,
            'include_html': self.incl_manager.render_include_html('novel_all', extra_data=extra_data,
                                                                  request_param_code=default_config),
        })

        return response
