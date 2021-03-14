from django.http import HttpResponse

from django_cms.models import HtmlPage
from django_cms.utils.cache_manager import CacheManager
from novel.models import NovelSetting
from novel.views.base import NovelBaseView


class PageView(NovelBaseView):
    template_name = "novel/page.html"

    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        page = HtmlPage.objects.filter(slug=slug, active=True).first()
        response = super().get(request, *args, **kwargs)
        if page:
            if page.type != 'html':
                return HttpResponse(page.content if page else '', content_type=page.type)

            response.context_data.update({
                'page_html': page.content if page else '',
            })

        return response

    @staticmethod
    def plain_text(request, page_type=None):
        novel_setting = CacheManager(NovelSetting).get_from_cache()
        if not page_type:
            return HttpResponse("", content_type='text/plain')

        plain_text = getattr(novel_setting, page_type, None) or ""
        return HttpResponse(plain_text, content_type='text/plain')
