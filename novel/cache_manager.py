from django_cms.utils.cache_manager import CacheManager


class NovelCache(CacheManager):
    def _get_data(self, **kwargs):
        return self.class_model.get_available_novel().filter(**kwargs).prefetch_related("novel_flat").all()
