from django.core.cache import cache
from django.utils.html import format_html_join
from django.utils.safestring import SafeString


class IncludeMapping(object):
    def __init__(self, mapping, request_url):
        self.TEMPLATE_INCLUDE_MAPPING = mapping
        self.request_url = request_url

    def render_include_html(self, template, extra_data=None, default='default'):
        if not extra_data:
            extra_data = {}

        if not template:
            return ""

        tmpl_incl_default = {}
        if template.includes_default and isinstance(template.includes_default, str):
            tmpl_incl_default = template.includes_default

        includes = template.include_template()

        mapping = self.TEMPLATE_INCLUDE_MAPPING
        inc_htmls = []
        for inc in includes:
            params = {}
            if inc.params:
                params = inc.params

            inc_params = params.get('default') or {}
            inc_params.update(params.get(tmpl_incl_default.get(inc.code) or default) or {})
            inc_func = mapping.get(inc.include_file)
            if inc_func:
                cache_enable = inc_params.get("cache_enabled") or False
                if cache_enable and self.request_url:
                    cache_key = self.request_url + inc.template.page_file + inc.code
                    html = cache.get(cache_key)
                    if not html or not repr(html):
                        inc_obj = inc_func(inc_params, extra_data)
                        html = format_html_join("\n", """<div class='{}'>{}</div>""",
                                                [(inc.class_name, inc_obj.render_html())])
                        cache.set(cache_key, html)
                else:
                    inc_obj = inc_func(inc_params, extra_data)
                    html = format_html_join("\n", """<div class='{}'>{}</div>""",
                                            [(inc.class_name, inc_obj.render_html())])
            else:
                html = format_html_join("\n", """
                                            <div class='mising-include-page'>Missing Include Page {}:{}</div>
                                """, [(inc.class_name, inc.include_file)])

            inc_htmls.append((html,))

        return format_html_join("", "{}", inc_htmls)
