from django.core.paginator import Paginator
from django.http import JsonResponse

from novel.models import Novel
from novel.views.base import NovelBaseView
from novel.widgets.chapter_list import ChapterListWidget
from novel.widgets.novel_grid import NovelGridWidget
from novel.widgets.novel_list import NovelListWidget


class NovelView(NovelBaseView):
    template_name = "novel/novel.html"
    content_type_mapping = {
        'latest_update': '-created_at',
    }

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        page = request.GET.get('page') or 1
        content_type = request.GET.get('type') or 'latest_update'
        view_type = request.GET.get('view') or 'list'

        order_by = self.content_type_mapping.get(content_type)
        novels = Novel.get_available_novel()

        if order_by:
            novels = novels.order_by(order_by)

        novels = novels.all()

        if novels:
            novels = Paginator(novels, 30)
            try:
                novels = novels.page(page)
            except:
                pass

        params = {
            'novels': novels, 'title': "LATEST NOVEL", 'fa_icon': "far fa-calendar-check",
        }
        novel_widget = NovelListWidget(**params) if view_type == 'list' else NovelGridWidget(**params)

        response.context_data.update({
            'novels': novel_widget,
            'view_type': view_type,
        })

        return response
