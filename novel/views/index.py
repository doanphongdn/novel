from django.core.paginator import Paginator

from novel.models import Novel
from novel.views.base import NovelBaseView
from novel.widgets.novel_grid import NovelGridWidget


class NovelIndexView(NovelBaseView):
    template_name = "novel/index.html"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        page = request.GET.get('page') or 1
        list_novel = Novel.get_available_novel().all()
        paginated = Paginator(list_novel, 12)
        try:
            paginated_data = paginated.page(page)
        except:
            paginated_data = None

        novel_grid = NovelGridWidget(novels=paginated_data, title="LATEST UPDATE", fa_icon="far fa-calendar-check")
        novel_list = NovelGridWidget(novels=paginated_data, title="HOT NOVEL", fa_icon="fab fa-hotjar")
        response.context_data.update({
            'novel_grid': novel_grid,
            'novel_list': novel_list,
        })

        return response
