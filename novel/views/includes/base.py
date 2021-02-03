from django.template import loader


class BaseTemplateInclude(object):
    cache = True
    name = None
    template = None
    default_values = {}

    def __init__(self, include_data, extra_data=None):
        self.include_data = include_data or {}

        # extra data must have key by code of include to support multi
        if extra_data and extra_data.get(self.name):
            self.include_data.update(extra_data.get(self.name))

        self.prepare_include_data()

    def prepare_include_data(self):
        pass

    def render_html(self):
        return loader.render_to_string(self.template, self.include_data)
