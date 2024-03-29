from django.contrib import sitemaps
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from novel.models import Novel, Genre, NovelChapter


class LimitSitemap(Sitemap):
    limit = 5000


class GenreSitemap(LimitSitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Genre.objects.all()


class NovelChapterSitemap(LimitSitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return NovelChapter.get_available_chapter().all()

    @classmethod
    def lastmod(cls, obj):
        return obj.updated_at


class NovelSitemap(LimitSitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Novel.get_available_novel().all()

    @classmethod
    def lastmod(cls, obj):
        return obj.updated_at


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['home']

    def location(self, item):
        return reverse(item)
