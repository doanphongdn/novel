from cms.models import Menu
from novel.cache_manager import MenuCache, GenreCache
from novel.models import Genre
from novel.views.includes.base import BaseTemplateInclude


class TopMenuTemplateInclude(BaseTemplateInclude):
    name = "menu"
    template = "novel/includes/base_top_menu.html"

    def __init__(self, include_data, extra_data=None):
        super().__init__(include_data, extra_data)

        menu_type = self.include_data.get('menu_type') or ''
        menu_data = self.include_data.get('menu_data') or MenuCache.get_all_from_cache(type=menu_type)

        genre_menu_enable = self.include_data.get("genre_menu_enable")
        genre_menu = {}
        if genre_menu_enable:
            genre_menu = {
                "name": self.include_data.get("genre_menu_name"),
                "icon": self.include_data.get("genre_menu_icon"),
                "data": []
            }
            genres = GenreCache.get_all_from_cache()
            for gen in genres:
                genre_menu["data"].append(gen)

        self.include_data = {
            "menu_data": menu_data,
            "genre_menu": genre_menu,
        }
