from django import forms


class ReportForm(forms.Form):
    novel_id = forms.CharField(required=False, widget=forms.HiddenInput(
        attrs={"class": "form-control", "id": "id_novel_report"}
    ))
    chapter_id = forms.CharField(required=False, widget=forms.HiddenInput(
        attrs={"class": "form-control", "id": "id_chapter_report"}
    ))

    content = forms.CharField(widget=forms.Textarea(
        attrs={"class": "form-control", "placeholder": "Content to report", "id": "id_content_report"}
    ))
