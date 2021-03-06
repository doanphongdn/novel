from django.http import HttpResponse

from django_cms.models import HtmlPage
from novel.views.base import NovelBaseView


class PageView(NovelBaseView):
    template_name = "novel/page.html"

    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        page = HtmlPage.objects.filter(slug=slug, active=True).first()
        if page.type != 'html':
            return HttpResponse(page.content if page else '', content_type=page.type)

        response = super().get(request, *args, **kwargs)
        response.context_data.update({
            'page_html': page.content if page else '',
        })
        return response
