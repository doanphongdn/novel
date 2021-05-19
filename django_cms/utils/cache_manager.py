from hashlib import md5

from django.core.cache import cache
from django.db.models import QuerySet
from django.utils.html import format_html_join


class CacheManager(object):
    def __init__(self, class_model,
                 cache_key=None, order_by=None, limit=None,
                 select_related=None, prefetch_related=None, **kwargs):
        if not order_by:
            order_by = ["pk"]
        elif isinstance(order_by, list):
            order_by.append("pk")
        else:
            order_by = [order_by]

        self.class_model = class_model
        self.kwargs = kwargs
        self.order_by = order_by
        self.limit = limit
        self.select_related = [select_related] if isinstance(select_related, str) else select_related
        self.prefetch_related = [prefetch_related] if isinstance(prefetch_related, str) else prefetch_related

        cache_keys = [str(val) for val in self.kwargs.values()]
        if class_model:
            cache_key = self.class_model.__name__
        elif not cache_key:
            cache_key = self.__class__.__name__

        self.cache_key = "CacheManager_" + md5("_".join((str(limit), str(cache_key), *cache_keys, *order_by)).encode()).hexdigest()

    def clear_cache(self):
        cache.delete(self.cache_key)

    def _get_data(self, **kwargs):
        if hasattr(self.class_model, 'active'):
            kwargs["active"] = True

        res = self.class_model.objects.filter(**kwargs).order_by(*self.order_by)
        if self.select_related:
            res = res.select_related(*self.select_related)

        if self.prefetch_related:
            res = res.prefetch_related(*self.prefetch_related)

        if self.limit and self.limit > 0:
            return res.all()[:self.limit]

        return res.all()

    def get_from_cache(self, get_all=False):
        try:
            cached = cache.get(self.cache_key)
            if cached is None:
                data = self._get_data(**self.kwargs)
                if data and isinstance(data, (QuerySet, list)) and not get_all:
                    data = data[0]

                cache.set(self.cache_key, data)
                return data

            return cached
        except Exception as e:
            print("[get_from_cache] Error when get data from cache %s" % e)
            import traceback
            traceback.print_exc()
            return {}


class IncludeHtmlCache(CacheManager):

    def __init__(self, include_obj, inc_params, extra_data, wrap_class_name, request=None, base_context=None):
        inc_params.update(extra_data)
        super().__init__(class_model=None, cache_key=include_obj.__name__, **inc_params)
        self.include_obj = include_obj
        self.inc_params = inc_params
        self.extra_data = extra_data
        self.wrap_class_name = wrap_class_name
        self.request = request
        self.base_context = base_context or {}

    def get_from_cache(self, get_all=True, **kwargs):
        cached = cache.get(self.cache_key)
        if cached is None:
            data = self._get_data(**kwargs)
            if not get_all:
                data = data[0]

            cache.set(self.cache_key, data)
            return data

        return cached

    def get_from_data(self, **kwargs):
        return self._get_data(**kwargs)

    def _get_data(self, **kwargs):
        if self.include_obj:
            inc_obj = self.include_obj(self.inc_params, self.extra_data,
                                       request=self.request, base_context=self.base_context)
            if self.wrap_class_name:
                return format_html_join("", "<div class='{}'>{}</div>",
                                        [(self.wrap_class_name, inc_obj.render_html())])
            else:
                return format_html_join("", "{}", [(inc_obj.render_html(),)])

        return format_html_join("", "<div class='include-error'>Nothing to include</div>", [])
