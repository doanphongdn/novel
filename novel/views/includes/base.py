from django.core.cache import cache
from django.template import loader


class BaseTemplateInclude(object):
    template = None

    def __init__(self):
        self.include_data = {}

    def render_html(self, caching_for=None):
        if caching_for:
            cached_html = cache.get(caching_for) or None
            if cached_html:
                return cached_html

        html = loader.render_to_string(self.template, self.include_data)
        if caching_for:
            cache.set(caching_for, html, 300)

        return html
