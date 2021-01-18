from novel.views.includes.base import BaseTemplateInclude


class PaginationTemplateInclude(BaseTemplateInclude):
    name = "pagination"
    template = "novel/includes/pagination.html"

    def __init__(self, include_data, extra_data=None):
        super().__init__(include_data, extra_data)
        self.include_data = {
            "paginated_data": self.include_data.get('paginated_data'),
            "page_label": self.include_data.get('page_label'),
        }
