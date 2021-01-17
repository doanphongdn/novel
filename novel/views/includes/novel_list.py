from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.urls import reverse

from novel.models import Novel
from novel.views.includes.__base import BaseTemplateInclude
from novel.views.includes.pagination import PaginationTemplateInclude


class NovelListTemplateInclude(BaseTemplateInclude):
    name = "novel_list"
    template = "novel/includes/novel_list.html"

    def __init__(self, include_data, extra_data=None):
        super().__init__(include_data, extra_data)

        view_type = self.include_data.get('view_type') or 'grid'
        show_button_type = self.include_data.get('show_button_type')
        show_button_view_all = self.include_data.get('show_button_view_all')
        paginate_enable = self.include_data.get('paginate_enable')
        order_by = self.include_data.get('order_by') or '-created_at'
        novel_type = self.include_data.get('novel_type') or 'latest-update'
        page = self.include_data.get('page') or 1
        limit = self.include_data.get('limit') or 12

        if show_button_type is None:
            show_button_type = True

        if show_button_view_all is None:
            show_button_view_all = True

        if paginate_enable is None:
            paginate_enable = True

        list_novel = Novel.get_available_novel().order_by(order_by).all()

        novel_paginated = []
        novel_paginating = Paginator(list_novel, limit)
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
            paging_data = {"paginated_data": novel_paginated, "page_label": "page"}
            pagination = PaginationTemplateInclude(paging_data)

        self.include_data = {
            "novels": novel_paginated,
            "title": self.include_data.get('title'),
            "view_type": view_type,
            "icon": self.include_data.get('icon'),
            "view_all_url": reverse("novel_all", kwargs={"novel_type": novel_type}) if show_button_view_all else "",
            "button_type_urls": button_type_urls,
            "pagination_html": pagination.render_html() if pagination else "",
        }
