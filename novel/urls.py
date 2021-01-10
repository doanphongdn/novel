"""crawl_service URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.views.decorators.cache import cache_page
from django.contrib.sitemaps import views as sitemaps_views

from novel.api.novel import APIViewNovelUpdateList, APIViewNovelChapterUpdateList
from novel.sitemap import NovelSitemap, StaticViewSitemap
from novel.views.chapter import ChapterView
from novel.views.index import NovelIndexView
from novel.views.novel_all import NovelView
from novel.views.novel import NovelDetailView

sitemaps = {
    'novels': NovelSitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('web/sitemap.xml', cache_page(86400)(sitemaps_views.index), {'sitemaps': sitemaps}),
    path('web/sitemap-<section>.xml', cache_page(86400)(sitemaps_views.sitemap), {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),

    path('api/novel/update_list', APIViewNovelUpdateList.as_view()),
    path('api/novel/chapter/update_list', APIViewNovelChapterUpdateList.as_view()),

    path('', NovelIndexView.as_view(), name="home"),
    path('novel/search', NovelDetailView.as_view()),
    path('novel', NovelView.as_view(), name="novel_view"),
    path('novel/<str:slug>', NovelDetailView.as_view(), name="novel"),
    path('novel/<str:slug>/<str:chapter_slug>', ChapterView.as_view(), name="chapter"),
]
