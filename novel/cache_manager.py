from django.core.cache import cache
from django.utils.html import format_html_join

from cms.models import PageTemplate, InludeTemplate
from novel.models import NovelSetting, Novel


class NovelCacheManager(object):
    name = None

    def _get_key(self, *args):
        key = (self.name, *args)
        return key

    def _get_data(self, **kwargs):
        return []

    def get_from_cache(self, **kwargs):
        cache_key = "_".join((self.name, *kwargs.values()))
        cached = cache.get(cache_key)
        if cached is None:
            data = self._get_data(**kwargs)
            cache.set(cache_key, data)
            return data

        return cached


class TemplateCache(NovelCacheManager):
    name = "cache_template"

    def _get_data(self, **kwargs):
        return PageTemplate.objects.filter(page_file=kwargs.get('page_tmpl_code')).first()


class IncludeCache(NovelCacheManager):
    name = "cache_include"

    def _get_data(self, **kwargs):
        return InludeTemplate.objects.filter(template__page_file=kwargs.get('page_tmpl_code'),
                                             active=True).order_by("priority").all()


class IncludeHtmlCache(NovelCacheManager):
    name = "cache_include_html"

    def __init__(self, include_obj, inc_params, extra_data, wrap_class_name):
        self.include_obj = include_obj
        self.inc_params = inc_params
        self.extra_data = extra_data
        self.wrap_class_name = wrap_class_name

    def _get_data(self, **kwargs):
        if self.include_obj:
            inc_obj = self.include_obj(self.inc_params, self.extra_data)
            return format_html_join("", "<div class='{}'>{}</div>", [(self.wrap_class_name, inc_obj.render_html())])

        return format_html_join("", "<div class='include-error'>Nothing to include</div>", [])


class NovelSettingCache(NovelCacheManager):
    name = "cache_novel_setting"

    def _get_data(self, **kwargs):
        return NovelSetting.get_setting()


class NovelCache(NovelCacheManager):
    name = "cache_novel"

    def _get_data(self, **kwargs):
        return Novel.get_available_novel().filter(slug=kwargs.get('slug')).first()

