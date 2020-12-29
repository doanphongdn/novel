from django.contrib import admin


# Register your models here.
from cms.models import HtmlPage


@admin.register(HtmlPage)
class NovelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "active", "created_at", "updated_at")
    search_fields = ("name", "slug")
    list_filter = ("active",)
