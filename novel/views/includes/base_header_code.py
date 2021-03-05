from django_cms.utils.cache_manager import CacheManager
from django_cms.models import FooterInfo
from novel.views.includes.base import BaseTemplateInclude


class FooterInfotemplateInclude(BaseTemplateInclude):
    name = "base_header_code"
    template = "novel/includes/base_header_code.html"

    def prepare_include_data(self):
        header_data = self.include_data.get("header_data") or []

        self.include_data.update({
            "content": ft_info and ft_info[0].content or "",
        })
