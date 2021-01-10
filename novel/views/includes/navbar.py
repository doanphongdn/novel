from novel.views.includes.base import BaseTemplateInclude


class NavBarTemplateInclude(BaseTemplateInclude):
    template = "novel/includes/navbar.html"

    def __init__(self, menus, title, logo):
        super().__init__()
        self.include_data = {
            "menus": menus,
            "title": title,
            "logo": logo,
        }
