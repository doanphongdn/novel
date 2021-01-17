import json

from django.utils.html import format_html_join

from novel.views.includes.breadcrumb import BreadCrumbTemplateInclude
from novel.views.includes.chapter_content import ChapterContentTemplateInclude
from novel.views.includes.chapter_list import ChapterListTemplateInclude
from novel.views.includes.footer_info import FooterInfoplateInclude
from novel.views.includes.link import LinkTemplateInclude
from novel.views.includes.novel_info import NovelInfoTemplateInclude
from novel.views.includes.novel_list import NovelListTemplateInclude
from novel.views.includes.pagination import PaginationTemplateInclude

TEMPLATE_INCLUDE_MAPPING = {
    "chapter_content": ChapterContentTemplateInclude,
    "chapter_list": ChapterListTemplateInclude,
    "link": LinkTemplateInclude,
    "novel_info": NovelInfoTemplateInclude,
    "novel_list": NovelListTemplateInclude,
    "breadcrumb": BreadCrumbTemplateInclude,
    "pagination": PaginationTemplateInclude,
    "footer_info": FooterInfoplateInclude,
}


class IncludeMapping(object):

    @classmethod
    def render_include_html(cls, template, extra_data=None, default='default'):
        if not extra_data:
            extra_data = {}

        if not template:
            return ""

        tmpl_incl_default = {}
        if template.includes_default and isinstance(template.includes_default, str):
            tmpl_incl_default = json.loads(template.includes_default, strict=False)

        includes = template.include_template()

        mapping = TEMPLATE_INCLUDE_MAPPING
        html = ""
        wrap_class = "container"
        inc_htmls = []
        for inc in includes:
            params = {}
            if inc.params:
                params = json.loads(inc.params, strict=True)

            inc_params = params.get('default') or {}
            inc_params.update(params.get(tmpl_incl_default.get(inc.code) or default) or {})

            inc_obj = mapping.get(inc.include_file)(inc_params, extra_data)
            wrap_class = inc.full_width and "container-fluid" or "container"
            inc_htmls.append((inc.class_name, inc_obj.render_html()))

        if inc_htmls:
            html = format_html_join("\n", "<div class='{}'>{}</div>", inc_htmls)

        if html:
            html = format_html_join("", "<div class='{}'><div class='row'>{}</div></div>", [(wrap_class, html)])

        return html
