from novel.views.includes.base import BaseTemplateInclude


class HashTagTemplateInclude(BaseTemplateInclude):
    template = "novel/includes/hashtag.html"

    def __init__(self, hashtag_data, hashtag_label='HashTags'):
        super().__init__()
        self.include_data = {
            "hashtag_data": hashtag_data,
            "hashtag_label": hashtag_label,
        }
