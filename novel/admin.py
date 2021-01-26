import zlib

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib import admin

from novel.models import Novel, NovelChapter, NovelSetting, Genre


class NovelForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'vLargeTextField', 'maxlength': 250}))
    url = forms.CharField(widget=forms.TextInput(attrs={'class': 'vLargeTextField', 'maxlength': 250}))
    thumbnail_image = forms.CharField(widget=forms.TextInput(attrs={'class': 'vLargeTextField', 'maxlength': 250}))
    follow = forms.IntegerField(widget=forms.NumberInput(attrs={'class': ''}))
    vote_total = forms.IntegerField(widget=forms.NumberInput(attrs={'class': ''}))
    view_total = forms.IntegerField(widget=forms.NumberInput(attrs={'class': ''}))
    view_daily = forms.IntegerField(widget=forms.NumberInput(attrs={'class': ''}))
    view_monthly = forms.IntegerField(widget=forms.NumberInput(attrs={'class': ''}))

    class Meta:
        model = Novel
        fields = '__all__'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "active")


@admin.register(Novel)
class NovelAdmin(admin.ModelAdmin):
    form = NovelForm
    list_display = ("id", "name", "novel_updated", "status",
                    "authors_name", "genres_name", "active", "created_at", "updated_at")
    search_fields = ("name", "slug")
    list_filter = ("status",)
    filter_horizontal = ("authors", "genres")


class NovelChapterForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'vLargeTextField', 'maxlength': 250}))
    url = forms.CharField(widget=forms.TextInput(attrs={'class': 'vLargeTextField', 'maxlength': 250}))
    content = forms.CharField(
        widget=CKEditorWidget(attrs={'style': 'width:100%;', 'cols': 80, 'rows': 10, 'class': ""}),
        required=False)

    class Meta:
        model = NovelChapter
        fields = '__all__'


@admin.register(NovelChapter)
class NovelChapterAdmin(admin.ModelAdmin):
    form = NovelChapterForm
    list_display = ("id", "name", "novel", "chapter_updated", "created_at", "updated_at")
    search_fields = ("name", "slug")

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


@admin.register(NovelSetting)
class NovelSettingAdmin(admin.ModelAdmin):
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
