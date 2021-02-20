from django import forms


class UserProfileForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(
        attrs={"class": "form-control"}
    ), max_length=30, required=False)
    last_name = forms.CharField(widget=forms.TextInput(
        attrs={"class": "form-control"}
    ), max_length=30)
    email = forms.CharField(widget=forms.TextInput(
        attrs={"class": "form-control"}
    ), required=True)
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            "autocomplete": "off",
            "class": "form-control",
        }
    ), required=False, min_length=6)
    re_password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            "autocomplete": "off",
            "class": "form-control",
        }
    ), required=False, min_length=6)
    avatar = forms.ImageField(widget=forms.FileInput(attrs={
        'onchange': 'upload_img(this);',
        'class': 'btn btn-success btn-sm',
        'hidden': 'true',
        'accept': 'image/*',
    }), required=False)
