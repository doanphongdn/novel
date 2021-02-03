from novel.views.includes.base import BaseTemplateInclude


class BreadCrumbTemplateInclude(BaseTemplateInclude):
    name = "breadcrumb"
    template = "novel/includes/breadcrumb.html"
