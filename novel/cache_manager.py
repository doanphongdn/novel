from django_cms.utils.cache_manager import CacheManager


class NovelCache(CacheManager):
    def _get_data(self, **kwargs):
        if self.limit and self.limit > 0:
            return self.class_model.get_available_novel().filter(
                **kwargs).prefetch_related("novel_flat").all()[:self.limit]
        return self.class_model.get_available_novel().filter(**kwargs).prefetch_related("novel_flat").all()


class ChapterCache(CacheManager):

    def _get_data(self, **kwargs):
        res_data = super(ChapterCache, self)._get_data(**kwargs)
        for data in res_data:
            data.binary_content = None

        return res_data
