from cms.models import Link, FooterInfo
from novel.views.includes.base import BaseTemplateInclude


class FooterInfoplateInclude(BaseTemplateInclude):
    name = "base_footer_info"
    template = "novel/includes/base_footer_info.html"

    def __init__(self, include_data, extra_data=None):
        super().__init__(include_data, extra_data)

        ft_copyright = ""
        ft_content = ""

        footer_info = FooterInfo.objects.filter(active=True).first()
        if footer_info:
            ft_copyright = footer_info.copyright
            ft_content = footer_info.content

        self.include_data = {
            "copyright": ft_copyright,
            "content": ft_content,
        }
