from cms.cache_manager import FooterInfoCache
from cms.models import Link, FooterInfo
from novel.views.includes.base import BaseTemplateInclude


class FooterInfotemplateInclude(BaseTemplateInclude):
    name = "base_footer_info"
    template = "novel/includes/base_footer_info.html"

    def __init__(self, include_data, extra_data=None):
        super().__init__(include_data, extra_data)

        footer_type = self.include_data.get("footer_type") or ""

        ft_copyright = FooterInfoCache.get_all_from_cache(type=footer_type)
        self.include_data = {
            "copyright": ft_copyright and ft_copyright.content or "",
        }
