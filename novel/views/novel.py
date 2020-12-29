from django.core.paginator import Paginator

from novel.models import Novel
from novel.views.base import NovelBaseView
from novel.widgets.novel_grid import NovelGridWidget


class NovelView(NovelBaseView):
    template_name = "novel/style1/novel.html"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        slug = kwargs.get('slug')
        novel = Novel.objects.filter(slug=slug).first()
        response.context_data.update({
            'novel': novel
        })
        return response
