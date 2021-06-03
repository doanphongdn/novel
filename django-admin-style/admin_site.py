from django.contrib import admin
from django.contrib.admin.apps import AdminConfig
from django.utils.translation import gettext_lazy
from django.views.decorators.cache import never_cache


class AdminSiteExt(admin.AdminSite):
    def __init__(self, name='admin'):
        super().__init__(name)
        delete_selected = self._actions.get("delete_selected")
        if delete_selected:
            delete_selected.short_description = gettext_lazy("Delete selected(s)")

    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        models = self._registry
        for model, model_admin in models.items():
            for app in app_list:
                for m in app.get("models"):
                    if m.get("object_name") == model._meta.object_name:
                        m["icon"] = getattr(model_admin, 'menu_icon', 'ri-arrow-right-s-line')

        return app_list

    def each_context(self, request):
        context = super().each_context(request)
        context["app_list"] = context.get("available_apps", [])
        return context

    @never_cache
    def index(self, request, extra_context=None):
        self.index_template = "admin/index.html"
        if not extra_context:
            extra_context = {}

        return super().index(request, extra_context)


class AdminConfigExt(AdminConfig):
    default_site = 'django-admin-style.admin_site.AdminSiteExt'

    def ready(self):
        super().ready()
