from novel.views.includes.base import BaseTemplateInclude


class BreadCrumbTemplateInclude(BaseTemplateInclude):
    template = "novel/includes/breadcrumb.html"

    def __init__(self, data):
        super().__init__()
        self.include_data = {
            "data": data,
        }
