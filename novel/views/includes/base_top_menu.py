from cms.models import Menu
from novel.models import Genre
from novel.views.includes.base import BaseTemplateInclude


class TopMenuTemplateInclude(BaseTemplateInclude):
    name = "menu"
    template = "novel/includes/base_top_menu.html"

    def __init__(self, include_data, extra_data=None):
        super().__init__(include_data, extra_data)

        menu_type = self.include_data.get('menu_type') or ''
        menu_data = self.include_data.get('menu_data') or Menu.objects.filter(type=menu_type, active=True).all()

        genre_menu_enable = self.include_data.get("genre_menu_enable")
        genre_menu = {}
        if genre_menu_enable:
            genre_menu = {
                "name": self.include_data.get("genre_menu_name"),
                "icon": self.include_data.get("genre_menu_icon"),
                "data": []
            }
            genres = Genre.get_available_genre().all()
            for gen in genres:
                genre_menu["data"].append(gen)

        self.include_data = {
            "menu_data": menu_data,
            "genre_menu": genre_menu,
        }
