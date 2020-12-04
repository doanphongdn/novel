from django.contrib import admin

from crawl_service.models import CrawlCampaign, CrawlItem, CrawlCondition, CrawlSource


class CrawlItemInlineAdmin(admin.TabularInline):
    model = CrawlItem
    extra = 0


class CrawlConditionInlineAdmin(admin.TabularInline):
    model = CrawlCondition
    extra = 0


@admin.register(CrawlCampaign)
class CrawlCampaignAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "source", "active")
    inlines = [
        CrawlItemInlineAdmin,
    ]


@admin.register(CrawlSource)
class CrawlSourceAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "homepage")
