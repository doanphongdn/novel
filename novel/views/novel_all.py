from cms.models import TemplateManager
from novel.views.base import NovelBaseView
from novel.views.includes.__mapping import IncludeMapping
from novel.views.includes.novel_list import NovelListTemplateInclude


class NovelView(NovelBaseView):
    template_name = "novel/novel_all.html"

    # content_type_mapping = {
    #     'latest-update': {
    #         'order_by': '-created_at',
    #         'icon': 'fa fa-calendar-check',
    #         'title': 'LATEST UPDATE',
    #     },
    #     'hot': {
    #         'order_by': '-created_at',
    #         'icon': 'fa fa-calendar-check',
    #     },
    # }

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        novel_type = kwargs.get('novel_type')
        tmpl = TemplateManager.objects.filter(page_file='novel_all').first()
        extra_data = {
            "novel_list": {
                "page": request.GET.get('page') or 1,
                "view_type": request.GET.get('view') or 'grid',
            }
        }
        response.context_data.update({
            'include_html': IncludeMapping.render_include_html(tmpl, extra_data=extra_data, default=novel_type),
        })

        return response
