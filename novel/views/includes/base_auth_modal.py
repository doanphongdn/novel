from novel.views.includes.base import BaseTemplateInclude


class BaseAuthModalTemplateInclude(BaseTemplateInclude):
    name = "base_auth_modal"
    template = "novel/includes/base_auth_modal.html"

    def __init__(self, include_data, extra_data=None):
        super().__init__(include_data, extra_data)

        self.include_data = {
            # "link_data": link_data,
            # "link_label": link_label,
        }
