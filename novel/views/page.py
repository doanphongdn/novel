from cms.models import HtmlPage
from novel.views.base import NovelBaseView


class PageView(NovelBaseView):
    template_name = "novel/page.html"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        slug = kwargs.get('slug')

        page = HtmlPage.objects.filter(slug=slug, type='novel').first()
        response.context_data.update({
            'page_html': page.content if page else '',
        })

        return response
