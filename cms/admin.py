from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib import admin
from django_json_widget.widgets import JSONEditorWidget

from cms.models import FooterInfo, Link, HtmlPage, PageTemplate, InludeTemplate, Menu


class HtmlPageForm(forms.ModelForm):
    content = forms.CharField(
        widget=CKEditorWidget(attrs={'style': 'width:100%;', 'cols': 80, 'rows': 10, 'class': ""}),
        required=False)

    class Meta:
        model = HtmlPage
        fields = '__all__'


class ActionAdmin(admin.ModelAdmin):
    actions = ["active", "deactive"]

    def active(self, request, queryset):
        for obj in queryset:
            obj.active = True
            obj.save()

    def deactive(self, request, queryset):
        for obj in queryset:
            obj.active = False
            obj.save()

    active.short_description = ">>>> V Active"
    deactive.short_description = "<<<< X Deactive"


@admin.register(HtmlPage)
class HtmlPageAdmin(ActionAdmin):
    form = HtmlPageForm
    list_display = ("id", "name", "active", "created_at", "updated_at")
    search_fields = ("name", "slug")
    list_filter = ("active",)


@admin.register(FooterInfo)
class FooterAdmin(admin.ModelAdmin):
    list_display = ("id", "active", "content")
    search_fields = ("content",)
    list_filter = ("active",)


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("id", "priority", "name", "url", "type")
    search_fields = ("name", "url", "type")
    list_filter = ("active", "type")


@admin.register(Link)
class LinkAdmin(ActionAdmin):
    list_display = ("id", "active", "name", "url", "type")
    search_fields = ("name", "url", "type")
    list_filter = ("active", "type")


class IncludeTemplateForm(forms.ModelForm):
    class Meta:
        model = InludeTemplate
        fields = ("template", "include_file", "priority", "code", "params", "class_name", "full_width", "active")
        widgets = {'params': JSONEditorWidget(options={
            'modes': ['code', 'tree'],
            'mode': 'tree',
            'search': False,
        }, attrs={
            "class": "vLargeTextField",
            "style": "height:400px; display:inline-block;",
        })}


@admin.register(InludeTemplate)
class InludeTemplateAdmin(ActionAdmin):
    list_display = ("template", "code", "include_file", "priority", "class_name", "full_width", "active")
    form = IncludeTemplateForm


class TemplateManagerForm(forms.ModelForm):
    class Meta:
        model = PageTemplate
        fields = ("page_file", "includes_default")
        widgets = {'includes_default': JSONEditorWidget}


@admin.register(PageTemplate)
class TemplateManagerAdmin(admin.ModelAdmin):
    list_display = ("id", "page_file")
    form = TemplateManagerForm
