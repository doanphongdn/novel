from cms.cache_manager import CacheManager


class NovelCache(CacheManager):
    def _get_data(self, **kwargs):
        if hasattr(self.class_model, 'get_available_novel'):
            raise AttributeError("%s no have function get_available_novel", self.class_model.__name__)
        return self.class_model.get_available_novel().filter(**kwargs).all()
