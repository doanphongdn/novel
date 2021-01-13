from django.contrib import admin

# Register your models here.
from cms.models import FooterInfo, HashTag, HtmlPage


@admin.register(HtmlPage)
class NovelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "active", "created_at", "updated_at")
    search_fields = ("name", "slug")
    list_filter = ("active",)


@admin.register(FooterInfo)
class FooterAdmin(admin.ModelAdmin):
    list_display = ("id", "active", "content", "copyright")
    search_fields = ("content", "copyright")
    list_filter = ("active",)


@admin.register(HashTag)
class HashTagAdmin(admin.ModelAdmin):
    list_display = ("id", "active", "name", "url", "type")
    search_fields = ("name", "url", "type")
    list_filter = ("active",)
