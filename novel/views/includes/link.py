from novel.views.includes.base import BaseTemplateInclude


class LinkTemplateInclude(BaseTemplateInclude):
    template = "novel/includes/link.html"

    def __init__(self, link_data, link_label='HashTags'):
        super().__init__()
        self.include_data = {
            "link_data": link_data,
            "link_label": link_label,
        }
