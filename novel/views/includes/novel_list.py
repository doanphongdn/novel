from urllib.parse import urlencode

from django.core.paginator import Paginator

from novel.views.includes.base import BaseTemplateInclude
from novel.views.includes.pagination import PaginationTemplateInclude


class NovelListTemplateInclude(BaseTemplateInclude):
    template = "novel/includes/novel_list.html"

    def __init__(self, novels, title, icon=None, view_type="grid",
                 view_all_url=None, show_button_type=False, paginate_enable=False, page=1, limit=12):
        super().__init__()

        novel_paginated = []
        novel_paginating = Paginator(novels, limit)
        try:
            novel_paginated = novel_paginating.page(page)
        except:
            pass

        button_type_urls = {}
        if show_button_type:
            params = {}
            if int(page) > 1:
                params = {'page': page}

            button_type_urls = {
                'grid': '#',
                'list': '#',
            }
            if view_type == 'list':
                params['view'] = 'grid'
                button_type_urls['grid'] = "?" + urlencode(params)

            elif view_type == 'grid':
                params['view'] = 'list'
                button_type_urls['list'] = "?" + urlencode(params)

        pagination = None
        if paginate_enable:
            pagination = PaginationTemplateInclude(**{"paginated_data": novel_paginated})

        self.include_data = {
            "novels": novel_paginated,
            "title": title,
            "item_type": view_type,
            "icon": icon,
            "view_all_url": view_all_url,
            "button_type_urls": button_type_urls,
            "pagination_html": pagination.render_html() if pagination else "",
        }
