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

from novel.api.novel import APIViewNovelUpdateList, APIViewNovelChapterUpdateList
from novel.views.index import NovelIndexView
from novel.views.novel import NovelView

urlpatterns = [
    path('api/novel/update_list', APIViewNovelUpdateList.as_view()),
    path('api/novel/chapter/update_list', APIViewNovelChapterUpdateList.as_view()),

    path('', NovelIndexView.as_view()),
    path('novel/<str:slug>', NovelView.as_view()),

]
