from django.core.paginator import Paginator

from novel.models import Novel
from novel.views.base import NovelBaseView
from novel.views.includes.novel_list import NovelListTemplateInclude


class NovelIndexView(NovelBaseView):
    template_name = "novel/index.html"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        list_novel = Novel.get_available_novel().all()

        include_data = {
            "novels": list_novel,
            "title": "LATEST UPDATE",
            "icon": "far fa-calendar-check",
        }
        novel_grid = NovelListTemplateInclude(**include_data)

        include_data.update({
            "title": "HOT NOVELS",
            "icon": "fab fa-hotjar",
            "item_type": "list",
        })
        novel_list = NovelListTemplateInclude(**include_data)

        response.context_data.update({
            'novel_grid_html': novel_grid.render_html(),
            'novel_list_html': novel_list.render_html(),
        })

        return response
