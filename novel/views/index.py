from django.core.paginator import Paginator
from django.urls import reverse

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
            "icon": "fa fa-calendar",
            "view_all_url": reverse("novel_all", kwargs={"type": "latest-update"}),
        }
        novel_grid = NovelListTemplateInclude(**include_data)

        include_data.update({
            "title": "HOT NOVELS",
            "icon": "fa fa-fire",
            "view_type": "list",
            "view_all_url": reverse("novel_all", kwargs={"type": "hot"}),
        })
        novel_list = NovelListTemplateInclude(**include_data)

        response.context_data.update({
            'novel_grid_html': novel_grid.render_html(),
            'novel_list_html': novel_list.render_html(),
        })

        return response
