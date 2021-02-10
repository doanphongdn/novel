from ckeditor.widgets import CKEditorWidget
from django import forms


class CommentForm(forms.Form):
    content = forms.CharField(
        widget=CKEditorWidget(config_name='comment'), required=True)
    name = forms.CharField(widget=forms.TextInput(
        attrs={"class": "form-control comment-name", "placeholder": "Name"}
    ), max_length=30)
    novel_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    chapter_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    parent_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    reply_id = forms.CharField(widget=forms.HiddenInput(), required=False)
