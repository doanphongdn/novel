import zlib

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.admin.views.main import ChangeList
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html
from django.views.decorators.cache import never_cache

from django_cms.admin import BaseActionAdmin
from django_cms.models import CDNServer
from novel.models import CDNNovelFile, Genre, Novel, NovelChapter, NovelSetting, Status, NovelReport, Comment


class NovelForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'vLargeTextField', 'maxlength': 250}))
    thumbnail_image = forms.CharField(required=False,
                                      widget=forms.TextInput(attrs={'class': 'vLargeTextField', 'maxlength': 250}))
    follow = forms.IntegerField(widget=forms.NumberInput(attrs={'class': ''}))
    vote_total = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': ''}))
    view_total = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': ''}))
    view_daily = forms.IntegerField(widget=forms.NumberInput(attrs={'class': ''}))
    view_monthly = forms.IntegerField(widget=forms.NumberInput(attrs={'class': ''}))

    class Meta:
        model = Novel
        fields = '__all__'


@admin.register(Novel)
class NovelAdmin(BaseActionAdmin):
    form = NovelForm
    list_display = ("id", "name", "novel_updated", "status", "active", "created_at", "updated_at")
    search_fields = ("name", "slug", "src_url")
    list_filter = ("status",)
    filter_horizontal = ("authors", "genres")
    actions = ["update_flat_info"]
    exclude = ["novel_flat"]

    def update_flat_info(self, request, queryset):
        for obj in queryset:
            obj.update_flat_info()
            obj.save()

    update_flat_info.short_description = "Update flat info"


class NovelChapterForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'vLargeTextField', 'maxlength': 250}))
    content = forms.CharField(
        widget=CKEditorWidget(attrs={'style': 'width:100%;', 'cols': 80, 'rows': 10, 'class': ""}),
        required=False)

    class Meta:
        model = NovelChapter
        fields = '__all__'


class CustomChangeList(ChangeList):
    def get_queryset(self, request):
        queryset = super(CustomChangeList, self).get_queryset(request)

        return queryset[:10000]


@admin.register(NovelChapter)
class NovelChapterAdmin(BaseActionAdmin):
    form = NovelChapterForm
    list_display = ("id", "name", "novel", "chapter_updated", "created_at", "updated_at")
    search_fields = ("novel__id", "novel__name", "novel_slug", "name", "slug")

    actions = ("chapter_updated_true", "chapter_updated_false")

    def get_changelist(self, request, **kwargs):
        return CustomChangeList

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        if obj and obj.binary_content:
            content_field = form.base_fields.get('content')
            content_decompresed = zlib.decompress(obj.binary_content).decode()
            content_field.initial = content_decompresed
            form.base_fields['content'] = content_field

        return form

    def save_model(self, request, obj, form, change):
        content = form.cleaned_data.get('content')
        if content:
            content = zlib.compress(content.encode())
        obj.binary_content = content or None
        super().save_model(request, obj, form, change)

    def chapter_updated_true(self, request, queryset):
        for obj in queryset:
            obj.chapter_updated = True
            obj.save()

    def chapter_updated_false(self, request, queryset):
        for obj in queryset:
            obj.chapter_updated = False
            obj.save()

    chapter_updated_true.short_description = "Chapter updated ->> TRUE"
    chapter_updated_false.short_description = "Chapter updated ->> FALSE"


@admin.register(NovelSetting)
class NovelSettingAdmin(BaseActionAdmin):
    list_display = (
        "id", "title", "favicon", "logo", "novel_type", "meta_keywords", "meta_description", "meta_copyright",
        "meta_author", "img_ignoring",
        "meta_img", "meta_og_type", "meta_og_description", "meta_fb_app_id",
        "google_analystics_id")

    fields = ["title", 'favicon_tag', "favicon", "novel_type", 'logo_tag', "logo", "meta_keywords", "meta_description",
              "meta_copyright", "meta_author", "meta_img", "meta_img_tag", "img_ignoring",
              "meta_og_type", "meta_og_description", "meta_fb_app_id",
              "google_analystics_id", ]
    readonly_fields = ['logo_tag', 'favicon_tag', 'meta_img_tag']


@admin.register(CDNNovelFile)
class CDNNovelFileAdmin(BaseActionAdmin):
    list_display = ("id", "cdn", "chapter", "type", "hash_origin_url", "retry", "full")
    search_fields = ("cdn", "chapter", "hash_origin_url", "url")
    readonly_fields = ("chapter",)


@admin.register(CDNServer)
class CDNServerAdmin(BaseActionAdmin):
    list_display = ("id", "name", "server_id", "endpoint", "last_run", "status")


class AdminSiteExt(admin.AdminSite):
    @never_cache
    def index(self, request, extra_context=None):
        """
        Add extra content and response
        """
        app_list = self.get_app_list(request)

        context = {
            **self.each_context(request),
            'title': self.index_title,
            'app_list': app_list,
            'teko_version': 111,
            **(extra_context or {}),
        }

        request.current_app = self.name

        return TemplateResponse(request, self.index_template or 'admin/index.html', context)


@admin.register(Status)
class StatusAdmin(BaseActionAdmin):
    list_display = ("id", "name", "active")


@admin.register(Genre)
class GenreAdmin(BaseActionAdmin):
    list_display = ("id", "name", "style_color", "slug", "active")


@admin.register(NovelReport)
class ReportAdmin(BaseActionAdmin):
    readonly_fields = ("user", "novel", "chapter", "content")
    list_display = ("id", "user", "novel_link", "chapter_link", "content")

    @staticmethod
    def novel_link(instance):
        url = reverse('admin:%s_%s_change' % (instance.novel._meta.app_label,
                                              instance.novel._meta.model_name), args=(instance.novel.id,))
        return format_html(u'<a href="{}">{}</a>', url, instance.novel)

    @staticmethod
    def chapter_link(instance):
        url = reverse('admin:%s_%s_change' % (instance.chapter._meta.app_label,
                                              instance.chapter._meta.model_name), args=(instance.chapter.id,))
        return format_html(u'<a href="{}">{}</a>', url, instance.chapter)


@admin.register(Comment)
class CommentAdmin(BaseActionAdmin):
    ordering = ("-id",)
    readonly_fields = ("novel", "chapter", "name", "content_html", "created_at")
    exclude = ("user", "parent_id", "reply_id", "content")
    list_display = ("id", "novel", "name", "content_html", "created_at")

    def content_html(self, obj):
        return format_html(obj.content)
