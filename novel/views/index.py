from django.core.paginator import Paginator

from novel.models import Novel
from novel.views.base import NovelBaseView


class NovelIndexView(NovelBaseView):
    template_name = "novel/style1/index.html"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        page = request.GET.get('page') or 1
        list_novel = Novel.get_available_novel().all()
        has_next = False
        paginated = Paginator(list_novel, 10)
        try:
            paginated_data = paginated.page(page)
        except:
            paginated_data = None

        if paginated_data:
            has_next = paginated_data.has_next()

        response.context_data.update({
            'novels': paginated_data,
            'has_next': has_next,
        })

        return response
