from novel.views.includes.base import BaseTemplateInclude


class NovelInfoTemplateInclude(BaseTemplateInclude):
    template = "novel/includes/novel_info.html"

    def __init__(self, novel):
        super().__init__()
        self.include_data = {
            "novel": novel,
        }
