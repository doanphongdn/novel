from cms.cache_manager import CacheManager
from cms.models import PageTemplate
from crawl_service import settings
from novel.models import Genre
from novel.views.base import NovelBaseView


class NovelAllView(NovelBaseView):
    template_name = "novel/novel_all.html"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        genre = kwargs.get('genre')
        novel_type = kwargs.get('novel_type')
        default_config = genre or novel_type

        tmpl = CacheManager(PageTemplate, **{"page_file": "novel_all"}).get_from_cache()
        extra_data = {
            "novel_list": {
                "page": request.GET.get('page') or 1,
                "view_type": request.GET.get('view') or 'grid',
            }
        }

        if genre:
            genre_pre_title = tmpl.params.get("genre_pre_title") or ""
            genre_obj = CacheManager(Genre, **{"slug": genre}).get_from_cache(get_all=True)[0]
            extra_data['novel_list'].update({
                "filter_by": {"genres__slug": genre},
                "title": genre_pre_title + " - " + genre_obj.name if genre_obj else settings.NOVEL_GENRE_URL.upper(),
                "icon": "fa fa-cubes",
            })

        response.context_data.update({
            'include_html': self.incl_manager.render_include_html('novel_all', extra_data=extra_data,
                                                                  request_param_code=default_config),
        })

        return response
