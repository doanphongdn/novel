from django.contrib import sitemaps
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.views.decorators.cache import cache_page

from novel.models import Novel, Genre, NovelChapter


class LimitSitemap(Sitemap):
    limit = 50000


class GenreSitemap(LimitSitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Genre.objects.all()


class NovelChapterSitemap(LimitSitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return NovelChapter.get_available_chapter().all()

    @classmethod
    def lastmod(cls, obj):
        return obj.updated_at


class NovelSitemap(LimitSitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Novel.get_available_novel().all()

    @classmethod
    def lastmod(cls, obj):
        return obj.updated_at


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return ['home']

    def location(self, item):
        return reverse(item)
