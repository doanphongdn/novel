from cms.models import TemplateManager
from novel.views.base import NovelBaseView
from novel.views.includes.__mapping import IncludeMapping


class NovelIndexView(NovelBaseView):
    template_name = "novel/index.html"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        tmpl = TemplateManager.objects.filter(page_file='index').first()
        index_include_html = IncludeMapping.render_include_html(tmpl)

        response.context_data.update({
            'index_include_html': index_include_html,
        })

        return response
