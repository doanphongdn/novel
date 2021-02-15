from django.contrib import admin

from cms.admin import ActionAdmin
from crawl_service.models import CDNServer, CrawlCampaign, CrawlItem, CrawlCampaignSource, CrawlItemAction, CrawlLog


#
#
# class ItemInlineFormSet(BaseInlineFormSet):
#     def clean(self):
#         super(ItemInlineFormSet, self).clean()
#         item_codes = []
#         for form in self.forms:
#             item_codes.append(form.cleaned_data.get('code'))
#
#         type_code = self.instance.campaign_type
#         campaign_type = StoryCampaignMapping.type_mapping.get(type_code)
#
#         item_codes = set(item_codes)
#         required_fields = set(campaign_type.required_fields)
#         required_missing_fields = required_fields - item_codes
#         if required_missing_fields:
#             raise ValidationError("<%s> codes is required" % ", ".join(list(required_missing_fields)))
#
#         no_defined_fields = item_codes - required_fields - set(campaign_type.optional_fields)
#         if no_defined_fields:
#             raise ValidationError("<%s> codes has not been defined in <%s> Campaign Type" % (
#                 ", ".join(list(no_defined_fields)), campaign_type.__name__))
#

class CrawlItemInlineAdmin(admin.TabularInline):
    model = CrawlItem
    extra = 0


class CrawlItemActionInlineAdmin(admin.TabularInline):
    model = CrawlItemAction
    extra = 0


class CrawlLogInlineAdmin(admin.TabularInline):
    model = CrawlLog
    readonly_fields = ("source_url", "crawled_data", "log")
    extra = 0

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.first()


@admin.register(CrawlCampaign)
class CrawlCampaignAdmin(ActionAdmin):
    list_display = ("name", "campaign_source", "campaign_type", "status", "last_run", "target_url", "active")
    # readonly_fields = ("status",)
    inlines = [
        CrawlItemInlineAdmin,
        CrawlItemActionInlineAdmin,
        CrawlLogInlineAdmin
    ]


@admin.register(CrawlCampaignSource)
class CrawlSourceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "homepage")


@admin.register(CDNServer)
class CDNServerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "server_id", "endpoint", "status")
