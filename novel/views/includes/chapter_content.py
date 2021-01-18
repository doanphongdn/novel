from novel.views.includes.base import BaseTemplateInclude


class ChapterContentTemplateInclude(BaseTemplateInclude):
    name = "chapter_content"
    template = "novel/includes/chapter_content.html"

    def __init__(self, include_data, extra_data=None):
        super().__init__(include_data, extra_data)
        self.include_data = {
            "chapter": self.include_data.get("chapter"),
        }
