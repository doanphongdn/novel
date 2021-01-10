from novel.models import Novel
from novel.views.base import NovelBaseView
from novel.views.includes.novel_list import NovelListTemplateInclude


class NovelView(NovelBaseView):
    template_name = "novel/novel_all.html"
    content_type_mapping = {
        'latest-update': '-created_at',
        'hot': '-view_total',
    }

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        page = request.GET.get('page') or 1
        content_type = request.GET.get('type') or 'latest-update'
        view_type = request.GET.get('view') or 'list'

        order_by = self.content_type_mapping.get(content_type)
        novels = Novel.get_available_novel()

        if order_by:
            novels = novels.order_by(order_by)

        novels = novels.all()
        novel_list = NovelListTemplateInclude(novels=novels, title="LATEST NOVEL", icon="far fa-calendar-check",
                                              item_type=view_type, limit=30, page=page, show_button_type=True,
                                              paginate_enable=True)

        response.context_data.update({
            'novel_list_html': novel_list.render_html(),
            'view_type': view_type,
        })

        return response
