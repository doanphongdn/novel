from cms.models import Link
from novel.views.includes.__base import BaseTemplateInclude


class LinkTemplateInclude(BaseTemplateInclude):
    name = "link"
    template = "novel/includes/link.html"

    def __init__(self, include_data, extra_data=None):
        super().__init__(include_data, extra_data)

        link_type = self.include_data.get('link_type') or ''
        link_label = self.include_data.get('link_label') or ''
        link_data = Link.objects.filter(type=link_type, active=True).all()

        self.include_data = {
            "link_data": link_data,
            "link_label": link_label,
        }
