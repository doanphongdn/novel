from cms.cache_manager import FooterInfoCache
from novel.views.includes.base import BaseTemplateInclude


class FooterInfotemplateInclude(BaseTemplateInclude):
    name = "base_footer_info"
    template = "novel/includes/base_footer_info.html"

    def prepare_include_data(self):
        footer_type = self.include_data.get("footer_type")
        ft_info = FooterInfoCache.get_from_cache(get_all=True, **{"type": footer_type})

        self.include_data.update({
            "content": ft_info and ft_info.content or "",
        })