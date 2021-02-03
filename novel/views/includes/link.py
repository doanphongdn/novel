from cms.cache_manager import CacheManager
from cms.models import Link
from novel.views.includes.base import BaseTemplateInclude


class LinkTemplateInclude(BaseTemplateInclude):
    name = "link"
    template = "novel/includes/link.html"

    def prepare_include_data(self):
        link_type = self.include_data.get('link_type')
        link_data = self.include_data.get('link_data',
                                          CacheManager(Link, **{"type": link_type}).get_from_cache(get_all=True))

        self.include_data.update({
            "link_data": link_data,
        })
