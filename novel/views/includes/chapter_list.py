from django.core.paginator import Paginator

from novel.views.includes.base import BaseTemplateInclude
from novel.views.includes.pagination import PaginationTemplateInclude


class ChapterListTemplateInclude(BaseTemplateInclude):
    template = "novel/includes/chapter_list.html"

    def __init__(self, chapters, title, icon=None, page=1, limit=30):
        super().__init__()
        chapters = Paginator(chapters, limit)
        try:
            chapters = chapters.page(page)
        except:
            pass

        pagination = PaginationTemplateInclude(**{"paginated_data": chapters, 'page_label': 'chapter-page'})

        self.include_data = {
            "chapters": chapters,
            "title": title,
            "icon": icon,
            "pagination_html": pagination.render_html(),
        }
