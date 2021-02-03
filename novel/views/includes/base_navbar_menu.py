from cms.cache_manager import CacheManager
from cms.models import Menu
from novel.views.includes.base import BaseTemplateInclude


class BaseNavbarTemplateInclude(BaseTemplateInclude):
    cache = False
    name = "base_navbar_menu"
    template = "novel/includes/base_navbar_menu.html"

    def prepare_include_data(self):
        enable_auth_menu = self.include_data.get("enable_auth_menu") or False
        menu_type = self.include_data.get("menu_type") or False
        navbar_menus = CacheManager(Menu, **{"type": menu_type}).get_from_cache(get_all=True)

        self.include_data.update({
            "enable_auth_menu": enable_auth_menu,
            "navbar_menus": navbar_menus,
        })
