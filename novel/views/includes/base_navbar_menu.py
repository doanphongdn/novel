from novel.cache_manager import MenuCache
from novel.views.includes.base import BaseTemplateInclude


class BaseNavbarTemplateInclude(BaseTemplateInclude):
    name = "base_navbar_menu"
    template = "novel/includes/base_navbar_menu.html"

    def prepare_include_data(self):
        enable_auth_menu = self.include_data.get("enable_auth_menu") or False
        menu_type = self.include_data.get("menu_type") or False
        navbar_menus = MenuCache.get_from_cache(get_all=True, **{"type": menu_type})

        self.include_data.update({
            "enable_auth_menu": enable_auth_menu,
            "navbar_menus": navbar_menus,
        })
