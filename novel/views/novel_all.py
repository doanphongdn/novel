from django.core.paginator import Paginator

from novel.models import Novel
from novel.views.base import NovelBaseView
from novel.views.includes.novel_list import NovelListTemplateInclude
from novel.views.includes.pagination import PaginationTemplateInclude


class NovelView(NovelBaseView):
    template_name = "novel/novel_all.html"
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

        novel_list = NovelListTemplateInclude(novels=novels, title="LATEST NOVEL", icon="far fa-calendar-check",
                                              item_type=view_type)
        pagination = PaginationTemplateInclude(**{"paginated_data": novels})

        response.context_data.update({
            'novel_list_html': novel_list.render_html(),
            'pagination_html': pagination.render_html(),
            'view_type': view_type,
        })

        return response
