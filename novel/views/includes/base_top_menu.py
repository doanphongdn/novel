from django_cms.utils.cache_manager import CacheManager
from django_cms.models import Menu
from novel.models import Genre
from novel.views.includes.base import BaseTemplateInclude


class TopMenuTemplateInclude(BaseTemplateInclude):
    cache = False
    name = "menu"
    template = "novel/includes/base_top_menu.html"

    def prepare_include_data(self):

        menu_type = self.include_data.get('menu_type')
        menu_data = self.include_data.get('menu_data',
                                          CacheManager(Menu, **{"type": menu_type}).get_from_cache(get_all=True))

        genre_menu = {}
        genre_menu_name = self.include_data.get("genre_menu_name")
        genre_menu_icon = self.include_data.get("genre_menu_icon")
        genre_menu_enable = self.include_data.get("genre_menu_enable")
        if genre_menu_enable:
            genre_menu = {
                "name": genre_menu_name,
                "icon": genre_menu_icon,
                "data": []
            }
            genres = CacheManager(Genre).get_from_cache(get_all=True)
            for gen in genres:
                genre_menu["data"].append(gen)

        self.include_data.update({
            "menu_data": menu_data,
            "genre_menu": genre_menu,
        })
