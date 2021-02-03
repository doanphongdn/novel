from cms.cache_manager import CacheManager
from novel.models import Genre
from novel.views.includes.base import BaseTemplateInclude


class NovelCatTemplateInclude(BaseTemplateInclude):
    name = "novel_cat"
    template = "novel/includes/novel_cat.html"

    def prepare_include_data(self):
        col_number = self.include_data.get('col_number', 2)
        genres = self.include_data.get("genres", CacheManager(Genre).get_from_cache(get_all=True))

        self.include_data.update({
            "col_number": col_number,
            "genres": genres,
        })
