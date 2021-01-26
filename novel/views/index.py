from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from cms.models import TemplateManager
from novel.views.base import NovelBaseView


class NovelIndexView(NovelBaseView):
    template_name = "novel/index.html"

    @method_decorator(cache_page(60 * 5), name='cache_index')
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        tmpl = TemplateManager.objects.filter(page_file='index').first()
        index_include_html = self.include_mapping.render_include_html(tmpl)

        response.context_data.update({
            'index_include_html': index_include_html,
        })

        return response
