from cms.models import PageTemplate
from novel.views.base import NovelBaseView


class NovelIndexView(NovelBaseView):
    template_name = "novel/index.html"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        index_include_html = self.incl_manager.render_include_html('index')

        response.context_data.update({
            'index_include_html': index_include_html,
        })

        return response
