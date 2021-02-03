from cms.cache_manager import CacheManager
from cms.models import Menu
from novel.models import NovelSetting, Novel, Genre, NovelChapter


class SettingCache(CacheManager):
    @classmethod
    def _get_data(cls, **kwargs):
        return NovelSetting.get_setting()


class NovelCache(CacheManager):
    @classmethod
    def _get_data(cls, **kwargs):
        return Novel.get_available_novel().filter(**kwargs).all()


class NovelChapterCache(CacheManager):
    pass


class MenuCache(CacheManager):
    @classmethod
    def _get_data(cls, **kwargs):
        return Menu.objects.filter(**kwargs, active=True).all()


class GenreCache(CacheManager):
    @classmethod
    def _get_data(cls, **kwargs):
        return Genre.get_available_genre(**kwargs)
