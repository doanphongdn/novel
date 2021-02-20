from cms.cache_manager import CacheManager
from cms.models import Menu
from novel.models import Genre
from novel.views.includes.base import BaseTemplateInclude


class BaseNavbarTemplateInclude(BaseTemplateInclude):
    cache = False
    name = "base_navbar_menu"
    template = "novel/includes/base_navbar_menu.html"

    def prepare_include_data(self):
        enable_auth_menu = self.include_data.get("enable_auth_menu") or False
        menu_type = self.include_data.get("menu_type") or False
        navbar_menus = CacheManager(Menu, **{"type": menu_type}).get_from_cache(get_all=True)

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

        user_menus = CacheManager(Menu, "priority", **{"type": "user_profile"}).get_from_cache(get_all=True)

        if "logout_label" not in self.include_data:
            self.include_data["logout_label"] = "Logout"

        self.include_data.update({
            "enable_auth_menu": enable_auth_menu,
            "navbar_menus": navbar_menus,
            "genre_menu": genre_menu,
            "user_menus": user_menus,
        })
