import zlib

from django import forms
from django.contrib import admin

from truyenhayho.models import Novel, NovelChapter


@admin.register(Novel)
class NovelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "chapter_updated", "status",
                    "authors_name", "genres_name", "active", "created_at", "updated_at")
    search_fields = ("name", "slug")
    list_filter = ("status",)


# class NovelChapterForm(forms.ModelForm):
#     content = forms.CharField(widget=forms.Textarea(), required=False)
#
#     class Meta:
#         model = NovelChapter
#         fields = '__all__'
#     #
# def clean(self):
#     cleaned_data = super().clean()
#     content = cleaned_data.pop('content', "")
#     compressed = zlib.compress(content.encode())
#     # cleaned_data['binary_content'] = compressed
#     return cleaned_data


@admin.register(NovelChapter)
class NovelChapterAdmin(admin.ModelAdmin):
    # form = NovelChapterForm
    list_display = ("id", "name", "novel", "content_updated", "created_at", "updated_at")
    search_fields = ("name", "slug")

