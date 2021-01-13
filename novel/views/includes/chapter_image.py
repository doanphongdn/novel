from novel.views.includes.base import BaseTemplateInclude


class ChapterImageTemplateInclude(BaseTemplateInclude):
    template = "novel/includes/chapter_image.html"

    def __init__(self, chapter):
        super().__init__()
        self.include_data = {
            "chapter": chapter,
        }
