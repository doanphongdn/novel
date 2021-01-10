from django.core.paginator import Paginator

from novel.views.includes.base import BaseTemplateInclude
from novel.views.includes.pagination import PaginationTemplateInclude


class NovelListTemplateInclude(BaseTemplateInclude):
    template = "novel/includes/novel_list.html"

    def __init__(self, novels, title, icon=None, item_type="grid",
                 view_all_url=None, show_button_type=False, paginate_enable=False, page=1, limit=12):
        super().__init__()

        novel_paginated = []
        novel_paginating = Paginator(novels, limit)
        try:
            novel_paginated = novel_paginating.page(page)
        except:
            pass

        pagination = None
        if paginate_enable:
            pagination = PaginationTemplateInclude(**{"paginated_data": novel_paginated})

        self.include_data = {
            "novels": novel_paginated,
            "title": title,
            "item_type": item_type,
            "icon": icon,
            "view_all_url": view_all_url,
            "show_button_type": show_button_type,
            "pagination_html": pagination.render_html() if pagination else "",
        }
