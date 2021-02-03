from hashlib import md5

from django.core.cache import cache
from django.utils.html import format_html_join

from cms.models import InludeTemplate, PageTemplate, FooterInfo, Link


class CacheManager(object):
    class_model = None
    order_by = None

    @classmethod
    def _get_data(cls, **kwargs):
        if hasattr(cls.class_model, 'active'):
            kwargs["active"] = True
        if cls.order_by:
            return cls.class_model.objects.filter(**kwargs).order_by(cls.order_by).all()

        return cls.class_model.objects.filter(**kwargs).all()

    @classmethod
    def get_from_cache(cls, get_all=False, **kwargs):
        kwargs_key = [str(val) for val in kwargs.values()]
        cache_key = "CacheManager_" + md5("_".join((cls.__name__, *kwargs_key)).encode()).hexdigest()
        cached = cache.get(cache_key)
        if cached is None:
            data = cls._get_data(**kwargs)
            if not get_all:
                data = data[0]

            cache.set(cache_key, data)
            return data

        return cached


class TemplateCache(CacheManager):
    class_model = PageTemplate


class IncludeCache(CacheManager):
    class_model = InludeTemplate
    order_by = "priority"


class IncludeHtmlCache(CacheManager):
    def __init__(self, include_obj, inc_params, extra_data, wrap_class_name):
        self.include_obj = include_obj
        self.inc_params = inc_params
        self.extra_data = extra_data
        self.wrap_class_name = wrap_class_name

    def get_from_cache(self, get_all=True, **kwargs):
        kwargs_key = [str(val) for val in kwargs.values()]
        cache_key = "CacheManager_" + md5("_".join((self.__class__.__name__, *kwargs_key)).encode()).hexdigest()
        cached = cache.get(cache_key)
        if cached is None:
            data = self._get_data(**kwargs)
            if not get_all:
                data = data[0]

            cache.set(cache_key, data)
            return data

        return cached

    def _get_data(self, **kwargs):
        if self.include_obj:
            inc_obj = self.include_obj(self.inc_params, self.extra_data)
            return format_html_join("", "<div class='{}'>{}</div>", [(self.wrap_class_name, inc_obj.render_html())])

        return format_html_join("", "<div class='include-error'>Nothing to include</div>", [])


class FooterInfoCache(CacheManager):
    class_model = FooterInfo


class LinkCache(CacheManager):
    class_model = Link
