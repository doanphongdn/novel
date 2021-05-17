from django_cms.utils.cache_manager import CacheManager


class NovelCache(CacheManager):
    def _get_data(self, **kwargs):
        res = self.class_model.get_available_novel().filter(
            **kwargs).order_by(*self.order_by).prefetch_related("novel_flat").all()

        if self.limit and self.limit > 0:
            return res[:self.limit]

        return res


class BookmarkCountCache(CacheManager):
    def _get_data(self, **kwargs):
        return self.class_model.objects.filter(**kwargs).count()
