"""django_cms URL Configuration

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
import os

from django.conf.urls import url
from django.contrib.sitemaps import views as sitemaps_views
from django.urls import path
from django.views.decorators.cache import cache_page

from django_cms import settings
from django_cms.utils.view_base import view_dmca_validation, view_google_site_verification
from novel.sitemap import GenreSitemap, NovelChapterSitemap, NovelSitemap, StaticViewSitemap
from novel.views import stream
from novel.views.api.novel import ChapterAPIView, NovelAPIView
from novel.views.chapter import ChapterView
from novel.views.includes.comment import CommentManager
from novel.views.index import NovelIndexView
from novel.views.novel import NovelAction, NovelDetailView
from novel.views.novel_all import NovelAllView
from novel.views.page import PageView
from novel.views.reset_password import ResetPasswordCompleteView, ResetPasswordConfirmView
from novel.views.user import UserAction, UserProfileView

sitemaps = {
    'genre': GenreSitemap,
    'static': StaticViewSitemap,
    'novels': NovelSitemap,
    'chapters': NovelChapterSitemap,
}

urlpatterns = [
    url(os.environ.get('GOOGLE_SITE_VERIFICATION', 'google-site-verification'), view_google_site_verification,
        name="google_verification"),
    url(os.environ.get('DMCA_VALIDATION_URL', 'dmca-validation.html'), view_dmca_validation,
        name="dmca_verification"),
    url(r'^robots\.txt$', PageView.plain_text, {"page_type": "robots_txt"}),
    url(r'^ads\.txt$', PageView.plain_text, {"page_type": "ads_txt"}),
    url(r'^clickaine\.txt$', PageView.plain_text, {"page_type": "clickaine"}),

    path('web/sitemap.xml', cache_page(86400)(sitemaps_views.index), {'sitemaps': sitemaps}),
    path('web/sitemap-<section>.xml', cache_page(86400)(sitemaps_views.sitemap), {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),

    # Fix authenticate
    path('account_email', UserAction.redirect_url, name="account_email"),
    path('account_login', UserAction.redirect_url, name="account_login"),
    path('account_signup', UserAction.redirect_url, name="account_signup"),
    path('account_logout', UserAction.user_logout, name="account_logout"),

    # API URL
    path('api/novels', NovelAPIView.as_view()),
    path('api/novels/<str:src_campaign_code>', NovelAPIView.as_view()),
    path('api/chapters', ChapterAPIView.as_view()),
    path('api/chapters/<str:src_campaign_code>', ChapterAPIView.as_view()),

    path('', NovelIndexView.as_view(), name="home"),
    path('search', NovelDetailView.as_view(), name="novel_search"),
    path('update_point', NovelDetailView.update_hot_point, name="novel_hot_point"),
    path(settings.NOVEL_ALL_URL, NovelAllView.as_view(), name="novel_view"),

    path('comment', CommentManager.comment, name="comment"),
    path('comment/form', CommentManager.comment_form, name="comment_form"),

    path('reset/<uidb64>/<token>/', ResetPasswordConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', ResetPasswordCompleteView.as_view(), name='password_reset_complete'),

    # Ajax
    path("user/reset-password", UserAction.password_reset_request, name='reset_password'),
    path("user/signup", UserAction.sign_up, name='user_sign_up'),
    path("user/signin", UserAction.sign_in, name='user_sign_in'),
    path("user/logout", UserAction.user_logout, name='user_logout'),
    path('user/bookmark', UserAction.bookmark, name='user_bookmark'),
    path('user/read_notify', UserAction.read_notify, name='user_read_notify'),
    path('user/novel-remove', UserAction.novel_remove, name='novel_remove'),
    path('novel/report', NovelAction.report_form, name="novel_report"),

    # must end of list
    path(settings.NOVEL_ALL_URL, NovelAllView.as_view(), name="novel_view"),
    path(settings.NOVEL_ALL_URL + '/<str:novel_type>', NovelAllView.as_view(), name="novel_all"),
    path(settings.NOVEL_GENRE_URL + '/<str:genre>', NovelAllView.as_view(), name="novel_genre"),
    path(settings.NOVEL_PAGE_URL + '/<str:slug>', PageView.as_view(), name="page_view"),
    path(settings.NOVEL_ACCOUNT_URL + '/<str:tab_name>', UserProfileView.as_view(), name="user_profile"),

    path('images/<str:novel_slug>/<str:chapter_slug>/<str:img>', stream.stream_image, name="stream_image"),
    path('images/thumbnail/<str:img>', stream.stream_image,
         name="stream_thumbnail_image"),

    path('<str:slug>', NovelDetailView.as_view(), name="novel"),
    path('<str:slug>/<str:chapter_slug>', ChapterView.as_view(), name="chapter"),
]
