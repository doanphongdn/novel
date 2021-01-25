from novel.models import Genre
from novel.views.includes.base import BaseTemplateInclude


class NovelCatTemplateInclude(BaseTemplateInclude):
    name = "novel_cat"
    template = "novel/includes/novel_cat.html"

    def __init__(self, include_data, extra_data=None):
        super().__init__(include_data, extra_data)
        genre_label = self.include_data.get('title') or ''
        col_number = self.include_data.get('col_number') or 2
        genres = self.include_data.get("genres") or Genre.objects.filter(active=True).all()

        self.include_data = {
            "col_number": col_number,
            "title": genre_label,
            "genres": genres,
        }
