from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet

from crawl_service.models import CrawlCampaign, CrawlItem, CrawlCampaignSource
from crawl_service.services.campaign_type import CrawlCampaignType


class ItemInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super(ItemInlineFormSet, self).clean()
        item_codes = []
        for form in self.forms:
            item_codes.append(form.cleaned_data.get('code'))

        type_code = self.instance.campaign_type
        campaign_type = CrawlCampaignType.type_mapping.get(type_code)

        item_codes = set(item_codes)
        required_fields = set(campaign_type.required_fields)
        required_missing_fields = required_fields - item_codes
        if required_missing_fields:
            raise ValidationError("<%s> codes is required" % ", ".join(list(required_missing_fields)))

        no_defined_fields = item_codes - required_fields - set(campaign_type.optional_fields)
        if no_defined_fields:
            raise ValidationError("<%s> codes has not been defined in <%s> Campaign Type" % (
                ", ".join(list(no_defined_fields)), campaign_type.__name__))


class CrawlItemInlineAdmin(admin.TabularInline):
    model = CrawlItem
    formset = ItemInlineFormSet
    extra = 0


@admin.register(CrawlCampaign)
class CrawlCampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "campaign_source", "campaign_type", "target_url", "active")
    inlines = [
        CrawlItemInlineAdmin,
    ]


@admin.register(CrawlCampaignSource)
class CrawlSourceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "homepage")
