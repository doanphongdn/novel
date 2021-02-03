from novel.views.includes.base import BaseTemplateInclude


class PaginationTemplateInclude(BaseTemplateInclude):
    name = "pagination"
    template = "novel/includes/pagination.html"
