from django import forms


class ReportContentForm(forms.Form):
    novel_id = forms.CharField(widget=forms.HiddenInput(
        attrs={"class": "form-control", }
    ))
    chapter_id = forms.CharField(widget=forms.HiddenInput(
        attrs={"class": "form-control", }
    ))

    content = forms.CharField(widget=forms.Textarea(
        attrs={"class": "form-control", "placeholder": "Content to report", }
    ))
