from urllib.parse import urlencode

from django.urls import reverse

from novel.paginator import NovelPaginator
from novel.views.includes.base import BaseTemplateInclude
from novel.views.includes.pagination import PaginationTemplateInclude


class NovelListTemplateInclude(BaseTemplateInclude):
    name = "novel_list"
    template = "novel/includes/novel_list.html"

    def prepare_include_data(self):
        filter_by = self.include_data.get('filter_by', {})
        view_type = self.include_data.get('view_type', 'grid')
        show_button_type = self.include_data.get('show_button_type')
        show_button_view_all = self.include_data.get('show_button_view_all')
        paginate_enable = self.include_data.get('paginate_enable')
        order_by = self.include_data.get('order_by') or '-created_at'
        novel_type = self.include_data.get('novel_type', 'latest-update')
        page = self.include_data.get('page') or 1
        limit = self.include_data.get('limit') or 12
        novel_list_col = self.include_data.get('novel_list_col') or 12
        novel_grid_col = self.include_data.get('novel_grid_col') or 4
        novel_grid_col_md = self.include_data.get('novel_grid_col_md') or 3
        novel_grid_col_lg = self.include_data.get('novel_grid_col_lg') or 2
        custom_chapters = self.include_data.get('custom_chapters') or {}

        css_class = {
            "novel_list_col": novel_list_col,
            "novel_grid_col": novel_grid_col,
            "novel_grid_col_md": novel_grid_col_md,
            "novel_grid_col_lg": novel_grid_col_lg
        }

        button_type_urls = {}
        if show_button_type is True:
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
        novel_paginated = NovelPaginator(limit, page, order_by, **filter_by)
        if paginate_enable is True:
            paging_data = {"paginated_data": novel_paginated, "page_label": "page"}
            pagination = PaginationTemplateInclude(paging_data)

        self.include_data.update({
            "novels": novel_paginated,
            "custom_chapters": custom_chapters,
            "view_type": view_type,
            "view_all_url": reverse("novel_all", kwargs={"novel_type": novel_type}) if show_button_view_all else "",
            "button_type_urls": button_type_urls,
            "pagination_html": pagination.render_html() if pagination else "",
            "css_class": css_class,
        })
