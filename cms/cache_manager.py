from django.core.cache import cache
from django.utils.html import format_html_join

from cms.models import InludeTemplate, PageTemplate, FooterInfo


class CacheManager(object):
    get_list = False

    @classmethod
    def _get_data(cls, **kwargs):
        return []

    @classmethod
    def get_first_from_cache(cls, **kwargs):
        lst_data = cls.get_all_from_cache(**kwargs)
        if lst_data:
            return lst_data[0]

        return None

    @classmethod
    def get_all_from_cache(cls, **kwargs):
        kwargs_key = [str(val) for val in kwargs.values()]
        cache_key = "_".join(("CacheManager_", cls.__name__, *kwargs_key))
        cached = cache.get(cache_key)
        if cached is None:
            data = cls._get_data(**kwargs)
            cache.set(cache_key, data)
            return data

        return cached


class TemplateCache(CacheManager):
    @classmethod
    def _get_data(cls, **kwargs):
        return PageTemplate.objects.filter(**kwargs).all()


class IncludeCache(CacheManager):
    @classmethod
    def _get_data(cls, **kwargs):
        return InludeTemplate.objects.filter(**kwargs, active=True).order_by("priority").all()


class IncludeHtmlCache(CacheManager):
    def __init__(self, include_obj, inc_params, extra_data, wrap_class_name):
        self.include_obj = include_obj
        self.inc_params = inc_params
        self.extra_data = extra_data
        self.wrap_class_name = wrap_class_name

    def get_first_from_cache(self, **kwargs):
        lst_data = self.get_all_from_cache(**kwargs)
        return lst_data

    def get_all_from_cache(self, **kwargs):
        cache_key = "_".join((self.__class__.__name__, *kwargs.values()))
        cached = cache.get(cache_key)
        if cached is None:
            data = self._get_data(**kwargs)
            cache.set(cache_key, data)
            return data

        return cached

    def _get_data(self, **kwargs):
        if self.include_obj:
            inc_obj = self.include_obj(self.inc_params, self.extra_data)
            return format_html_join("", "<div class='{}'>{}</div>", [(self.wrap_class_name, inc_obj.render_html())])

        return format_html_join("", "<div class='include-error'>Nothing to include</div>", [])


class FooterInfoCache(CacheManager):
    @classmethod
    def _get_data(cls, **kwargs):
        return FooterInfo.objects.filter(**kwargs, active=True).all()
