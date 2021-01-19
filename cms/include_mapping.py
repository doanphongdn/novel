from django.utils.html import format_html_join


class IncludeMapping(object):
    def __init__(self, mapping):
        self.TEMPLATE_INCLUDE_MAPPING = mapping

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
            inc_obj = mapping.get(inc.include_file)(inc_params, extra_data)

            html = format_html_join("\n", """
                <div class='container'>
                    <div class='row'>
                        <div class='{}'>{}</div>
                    </div>
                </div>
            """, [(inc.class_name, inc_obj.render_html())])

            inc_htmls.append((html,))

        return format_html_join("", "{}", inc_htmls)