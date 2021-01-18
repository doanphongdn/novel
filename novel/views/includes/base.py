import json

from django.template import loader


class BaseTemplateInclude(object):
    name = None
    template = None

    def __init__(self, include_data, extra_data=None):
        self.include_data = include_data or {}
        if extra_data and extra_data.get(self.name):
            self.include_data.update(extra_data.get(self.name))

    def render_html(self):
        return loader.render_to_string(self.template, self.include_data)
