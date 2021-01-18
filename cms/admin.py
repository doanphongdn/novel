from django import forms
from django.contrib import admin
from django_json_widget.widgets import JSONEditorWidget

from cms.models import FooterInfo, Link, HtmlPage, TemplateManager, InludeTemplate


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


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ("id", "active", "name", "url", "type")
    search_fields = ("name", "url", "type")
    list_filter = ("active",)


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
class InludeTemplateAdmin(admin.ModelAdmin):
    list_display = ("template", "code", "include_file", "priority", "class_name", "full_width", "active")
    form = IncludeTemplateForm


class TemplateManagerForm(forms.ModelForm):
    class Meta:
        model = TemplateManager
        fields = ("page_file", "includes_default")
        widgets = {'includes_default': JSONEditorWidget}


@admin.register(TemplateManager)
class TemplateManagerAdmin(admin.ModelAdmin):
    list_display = ("id", "page_file")
    form = TemplateManagerForm
