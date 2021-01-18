from novel.views.includes.base import BaseTemplateInclude


class BreadCrumbTemplateInclude(BaseTemplateInclude):
    name = "breadcrumb"
    template = "novel/includes/breadcrumb.html"

    def __init__(self, include_data, extra_data=None):
        super().__init__(include_data, extra_data)
        self.include_data = {
            "breadcrumb_data": self.include_data.get("breadcrumb_data"),
        }
