from django.template import loader


class BaseTemplateInclude(object):
    template = None

    def __init__(self):
        self.include_data = {}

    def render_html(self):
        return loader.render_to_string(self.template, self.include_data)
