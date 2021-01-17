from novel.views.includes.__base import BaseTemplateInclude


class NovelInfoTemplateInclude(BaseTemplateInclude):
    name = "novel_info"
    template = "novel/includes/novel_info.html"

    def __init__(self, include_data, extra_data=None):
        super().__init__(include_data, extra_data)
        self.include_data = {
            "novel": self.include_data.get("novel"),
        }
