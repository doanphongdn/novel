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
from django.contrib import admin
from django.urls import path, include

# NOTE: not working
# from django.conf.urls import handler404, handler500
# from django_cms.views.base import view_404

urlpatterns = [
    path('accounts/', include('custom_allauth.urls')),
    path('myadmin/login', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', include('novel.urls')),
    path('', include('django_backblaze_b2.urls')),
]

handler404 = 'django_cms.utils.view_base.view_404'
