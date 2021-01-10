from novel.views.includes.base import BaseTemplateInclude


class PaginationTemplateInclude(BaseTemplateInclude):
    template = "novel/includes/pagination.html"

    def __init__(self, paginated_data, page_label='page'):
        super().__init__()
        self.include_data = {
            "paginated_data": paginated_data,
            "page_label": page_label,
        }
