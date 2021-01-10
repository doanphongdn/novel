from novel.views.includes.base import BaseTemplateInclude


class ChapterContentTemplateInclude(BaseTemplateInclude):
    template = "novel/includes/chapter_content.html"

    def __init__(self, chapter):
        super().__init__()
        self.include_data = {
            "chapter": chapter,
        }
