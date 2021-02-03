from cms.cache_manager import CacheManager
from cms.models import Menu
from novel.models import NovelSetting, Novel, Genre


class SettingCache(CacheManager):
    class_model = NovelSetting


class NovelCache(CacheManager):
    @classmethod
    def _get_data(cls, **kwargs):
        return Novel.get_available_novel().filter(**kwargs).all()


class NovelChapterCache(CacheManager):
    pass


class MenuCache(CacheManager):
    class_model = Menu


class GenreCache(CacheManager):
    class_model = Genre
