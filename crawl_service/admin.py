from django.contrib import admin

from crawl_service.models import CrawlCampaign, CrawlItem


class CrawlItemInlineAdmin(admin.TabularInline):
    model = CrawlItem
    extra = 0


@admin.register(CrawlCampaign)
class CrawlCampaignAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "source_url", "pagination", "page_format")
    inlines = [
        CrawlItemInlineAdmin,
    ]
