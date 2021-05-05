from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig


class CmsConfig(AppConfig):
    name = 'django_cms'


class AdminConfigExt(AdminConfig):
    default_site = 'novel.admin.AdminSiteExt'

    def ready(self):
        super().ready()
