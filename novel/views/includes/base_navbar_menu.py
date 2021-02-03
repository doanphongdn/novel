from novel.views.includes.base import BaseTemplateInclude


class BaseNavbarTemplateInclude(BaseTemplateInclude):
    name = "base_navbar_menu"
    template = "novel/includes/base_navbar_menu.html"

    def __init__(self, include_data, extra_data=None):
        super().__init__(include_data, extra_data)

        enable_auth_menu = self.include_data.get("enable_auth_menu") or False

        self.include_data = {
            "enable_auth_menu": enable_auth_menu,
        }
