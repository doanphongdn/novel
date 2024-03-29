from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib import admin
from django_json_widget.widgets import JSONEditorWidget
from import_export.admin import ImportExportModelAdmin

from django_cms.models import FooterInfo, Link, HtmlPage, PageTemplate, InludeTemplate, Menu


class HtmlPageForm(forms.ModelForm):
    content = forms.CharField(
        widget=CKEditorWidget(attrs={'style': 'width:100%;', 'cols': 80, 'rows': 10, 'class': ""}),
        required=False)

    class Meta:
        model = HtmlPage
        fields = '__all__'


class BaseActionAdmin(admin.ModelAdmin):
    actions = ["duplicate"]

    def duplicate(self, request, queryset):
        for obj in queryset:
            obj.id = None
            obj.save()

    duplicate.short_description = "Duplicate selected record"


class ActionAdmin(BaseActionAdmin):
    actions = ["active", "deactive"]

    def active(self, request, queryset):
        for obj in queryset:
            obj.active = True
            obj.save()

    def deactive(self, request, queryset):
        for obj in queryset:
            obj.active = False
            obj.save()

    active.short_description = "Active selected record"
    deactive.short_description = "Deactive selected record"


@admin.register(HtmlPage)
class HtmlPageAdmin(ActionAdmin):
    menu_icon = "ri-pages-fill"
    form = HtmlPageForm
    list_display = ("id", "name", "active", "created_at", "updated_at")
    search_fields = ("name", "slug")
    list_filter = ("active",)


@admin.register(FooterInfo)
class FooterAdmin(BaseActionAdmin):
    menu_icon = "ri-layout-bottom-fill"
    list_display = ("id", "active", "content")
    search_fields = ("content",)
    list_filter = ("active",)


@admin.register(Menu)
class MenuAdmin(BaseActionAdmin, ImportExportModelAdmin):
    menu_icon = "ri-menu-2-fill"
    list_display = ("id", "priority", "name", "url", "type")
    search_fields = ("name", "url", "type")
    list_filter = ("active", "type")


@admin.register(Link)
class LinkAdmin(ActionAdmin, ImportExportModelAdmin):
    menu_icon = "ri-link"
    list_display = ("id", "active", "name", "url", "type")
    search_fields = ("name", "url", "type")
    list_filter = ("active", "type")


class IncludeTemplateForm(forms.ModelForm):
    class Meta:
        model = InludeTemplate
        fields = ("template", "include_file", "priority", "code", "params", "class_name", "active")
        widgets = {'params': JSONEditorWidget(options={
            'modes': ['code', 'tree'],
            'mode': 'tree',
            'search': False,
        }, attrs={
            "class": "vLargeTextField",
            "style": "height:400px; display:inline-block;",
        })}


@admin.register(InludeTemplate)
class InludeTemplateAdmin(ActionAdmin, ImportExportModelAdmin):
    menu_icon = "ri-dashboard-fill"
    list_display = ("template", "code", "include_file", "priority", "class_name", "active")
    form = IncludeTemplateForm


class TemplateManagerForm(forms.ModelForm):
    class Meta:
        model = PageTemplate
        fields = ("page_file", "params")
        widgets = {'params': JSONEditorWidget}


@admin.register(PageTemplate)
class TemplateManagerAdmin(BaseActionAdmin, ImportExportModelAdmin):
    menu_icon = "ri-layout-masonry-fill"
    list_display = ("id", "page_file")
    form = TemplateManagerForm
