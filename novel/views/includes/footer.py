from novel.views.includes.base import BaseTemplateInclude


class FooterTemplateInclude(BaseTemplateInclude):
    template = "novel/includes/footer.html"

    def __init__(self):
        super().__init__()
