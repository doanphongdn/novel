from hashlib import md5

from django.core.cache import cache
from django.utils.html import format_html_join


class CacheManager(object):
    def __init__(self, class_model, order_by: str = None, **kwargs):
        self.class_model = class_model
        self.kwargs = kwargs

    def _get_data(self, **kwargs):
        if hasattr(self.class_model, 'active'):
            kwargs["active"] = True

        return self.class_model.objects.filter(**kwargs).all()

    def get_from_cache(self, get_all=False):
        kwargs_key = [str(val) for val in self.kwargs.values()]

        cache_key = "CacheManager_" + md5("_".join((self.class_model.__name__, *kwargs_key)).encode()).hexdigest()
        cached = cache.get(cache_key)
        if cached is None:
            data = self._get_data(**self.kwargs)
            if data and not get_all:
                data = data[0]

            cache.set(cache_key, data)
            return data

        return cached


class IncludeHtmlCache(CacheManager):

    def __init__(self, include_obj, inc_params, extra_data, wrap_class_name, request=None):
        super().__init__(None)
        self.include_obj = include_obj
        self.inc_params = inc_params
        self.extra_data = extra_data
        self.wrap_class_name = wrap_class_name
        self.request = request

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

    def get_from_data(self, **kwargs):
        return self._get_data(**kwargs)

    def _get_data(self, **kwargs):
        if self.include_obj:
            inc_obj = self.include_obj(self.inc_params, self.extra_data)
            return format_html_join("", "<div class='{}'>{}</div>",
                                    [(self.wrap_class_name, inc_obj.render_html(request=self.request))])

        return format_html_join("", "<div class='include-error'>Nothing to include</div>", [])
