from django.core.paginator import Paginator

from cms.models import Link
from novel.views.includes.base import BaseTemplateInclude
from novel.views.includes.link import LinkTemplateInclude
from novel.views.includes.pagination import PaginationTemplateInclude


class ChapterListTemplateInclude(BaseTemplateInclude):
    name = "chapter_list"
    template = "novel/includes/chapter_list.html"

    def __init__(self, include_data, extra_data=None):
        super().__init__(include_data, extra_data)
        chapters = self.include_data.get("chap_data") or []
        limit = self.include_data.get("limit") or 30
        page = self.include_data.get("chap_page") or 1
        title = self.include_data.get("title")
        info_title = self.include_data.get("info_title")
        info_icon = self.include_data.get("info_icon")
        icon = self.include_data.get("icon")
        novel = self.include_data.get("novel")

        chapters = Paginator(chapters, limit)
        try:
            chapters = chapters.page(page)
        except:
            pass

        paging_data = {"paginated_data": chapters, "page_label": "chap-page"}
        pagination = PaginationTemplateInclude(paging_data)

        link_objs = Link.objects.filter(type=self.include_data.get('hashtags_link_type'), active=True).all()
        link_data = [
            {
                "name": novel.name + " " + link.name,
                "url": novel.get_absolute_url(),
                'class_name': link.class_name
            }
            for link in link_objs
        ]

        hashtags = LinkTemplateInclude(include_data={
            'link_data': link_data,
            'link_label': self.include_data.get('hashtags_link_label'),
        })

        self.include_data = {
            "chapters": chapters,
            "title": title,
            "info_title": info_title,
            "info_icon": info_icon,
            "icon": icon,
            "pagination_html": pagination.render_html(),
            "hashtags_html": hashtags.render_html(),
        }
