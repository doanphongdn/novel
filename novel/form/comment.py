from ckeditor.widgets import CKEditorWidget
from django import forms


class CommentForm(forms.Form):
    content = forms.CharField(
        widget=CKEditorWidget(config_name='comment'),
        required=False)
    name = forms.CharField(widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Name"}
    ), max_length=30)
