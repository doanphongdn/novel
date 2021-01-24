from cms.models import Link
from novel.views.includes.base import BaseTemplateInclude


class LinkTemplateInclude(BaseTemplateInclude):
    name = "top_menu"
    template = "novel/includes/top_menu.html"

    def __init__(self, include_data, extra_data=None):
        super().__init__(include_data, extra_data)

        link_type = self.include_data.get('link_type') or ''
        link_label = self.include_data.get('link_label') or ''
        link_data = self.include_data.get('link_data') or Link.objects.filter(type=link_type, active=True).all()

        self.include_data = {
            "link_data": link_data,
            "link_label": link_label,
        }
