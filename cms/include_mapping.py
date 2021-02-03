from hashlib import md5

from django.utils.html import format_html_join

from cms.cache_manager import TemplateCache, IncludeCache, IncludeHtmlCache


class IncludeManager(object):
    CACHE_TEMPLATE = {}

    def __init__(self, mapping):
        self.TEMPLATE_INCLUDE_MAPPING = mapping
        self.request_hash = None

    def set_request_hash(self, request):
        """
        Set unique hash for each request from client to caching
        :param request: client request from view
        """
        self.request_hash = md5(request.build_absolute_uri().encode("utf-8")).hexdigest()

    def render_include_html(self, tmpl_code, extra_data=None, default='default', cache=True):
        if not extra_data:
            extra_data = {}

        if not tmpl_code:
            return ""

        # Get template from cache
        template = TemplateCache.get_from_cache(page_file=tmpl_code)
        includes = IncludeCache.get_from_cache(get_all=True, template__page_file=tmpl_code)

        inc_htmls = []
        for inc in includes:
            # Get incude param default from code in template.includes_default of template
            # default code must be begin with default_<include_code>
            default_param = inc.params.get(template.includes_default.get("default_" + inc.code) or default) or {}
            # Get default param of include template
            inc_params = inc.params.get('default') or {}
            # Update override default param by dynamic param from request or nothing if dynamic = default
            inc_params.update(default_param)
            # Get include object from mapping
            inc_func = self.TEMPLATE_INCLUDE_MAPPING.get(inc.include_file)
            # Get render html from cache
            incl_html_cache = IncludeHtmlCache(inc_func, inc_params, extra_data, inc.class_name)
            html = incl_html_cache.get_from_cache(request_hash=self.request_hash,
                                                  page_tmpl_code=tmpl_code,
                                                  include_code=inc.code)
            inc_htmls.append((html,))

        return format_html_join("", "{}", inc_htmls)

    def get_include_htmls(self, tmpl_codes):
        return {code: self.render_include_html(code) for code in tmpl_codes}
