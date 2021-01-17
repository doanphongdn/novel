from django.core.paginator import Paginator

from novel.views.includes.__base import BaseTemplateInclude
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
        icon = self.include_data.get("icon")

        chapters = Paginator(chapters, limit)
        try:
            chapters = chapters.page(page)
        except:
            pass

        paging_data = {"paginated_data": chapters, "page_label": "chap-page"}
        pagination = PaginationTemplateInclude(paging_data)

        self.include_data = {
            "chapters": chapters,
            "title": title,
            "icon": icon,
            "pagination_html": pagination.render_html(),
        }
