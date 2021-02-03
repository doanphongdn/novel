from cms.cache_manager import CacheManager
from cms.models import FooterInfo
from novel.views.includes.base import BaseTemplateInclude


class FooterInfotemplateInclude(BaseTemplateInclude):
    name = "base_footer_info"
    template = "novel/includes/base_footer_info.html"

    def prepare_include_data(self):
        footer_type = self.include_data.get("footer_type")

        ft_info = CacheManager(FooterInfo, **{"type": footer_type}).get_from_cache(get_all=True)

        self.include_data.update({
            "content": ft_info and ft_info.content or "",
        })
