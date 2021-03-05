from hashlib import md5

from django.utils.html import format_html_join

from django_cms.utils.cache_manager import CacheManager, IncludeHtmlCache
from django_cms.models import PageTemplate, InludeTemplate


class IncludeManager(object):
    CACHE_TEMPLATE = {}

    def __init__(self, mapping):
        self.TEMPLATE_INCLUDE_MAPPING = mapping
        self.request_hash = None

    @classmethod
    def get_page_template(cls, tmpl_code):
        # Get template from cache
        template = CacheManager(PageTemplate, **{"page_file": tmpl_code}).get_from_cache()
        return template

    def set_request_hash(self, request):
        """
        Set unique hash for each request from client to caching
        :param request: client request from view
        """
        self.request_hash = md5(request.build_absolute_uri().encode("utf-8")).hexdigest()

    def render_include_html(self, tmpl_code, extra_data=None, request_param_code=None, request=None):
        if not extra_data:
            extra_data = {}

        if not tmpl_code:
            return ""

        # Get template from cache
        template = CacheManager(PageTemplate, **{"page_file": tmpl_code}).get_from_cache()
        includes = CacheManager(InludeTemplate, 'priority',
                                **{"template__page_file": tmpl_code}).get_from_cache(get_all=True)

        inc_htmls = []
        for inc in includes:
            # Get param by code from request
            request_param = request_param_code and inc.params.get(request_param_code) or {}
            # Get default param of include template
            default_param = inc.params.get('default') or {}
            # Update request params
            default_param.update(request_param)
            # Update template param
            default_param.update(template.params or {})

            # Get include object from mapping
            inc_func = self.TEMPLATE_INCLUDE_MAPPING.get(inc.include_file)
            # Get render html from cache
            incl_html_cache = IncludeHtmlCache(inc_func, default_param, extra_data, inc.class_name, request=request)
            if inc_func and inc_func.cache:
                html = incl_html_cache.get_from_cache(request_hash=self.request_hash, page_tmpl_code=tmpl_code,
                                                      include_code=inc.code)
            else:
                html = incl_html_cache.get_from_data() if incl_html_cache else 'Missing incl_html_cache'

            inc_htmls.append((html,))

        return format_html_join("", "{}", inc_htmls)

    def get_include_htmls(self, tmpl_codes, request=None):
        return {code: self.render_include_html(code, request=request) for code in tmpl_codes}
