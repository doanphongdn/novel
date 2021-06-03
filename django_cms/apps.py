from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig


class CmsConfig(AppConfig):
    name = 'django_cms'
    verbose_name = "Django CMS"


class AdminConfigExt(AdminConfig):
    default_site = 'novel.admin.AdminSiteExt'

    def ready(self):
        super().ready()


class AuthConfig(AppConfig):
    name = 'django.contrib.auth'
    verbose_name = "System Administrator"
