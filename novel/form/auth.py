from django import forms


class RegisterForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Name"}
    ), max_length=30)
    email = forms.CharField(widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Email", "type": "email"}
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            "autocomplete": "off",
            "class": "form-control",
            "type": "password",
            "placeholder": "Password",
        }
    ), min_length=6)
    re_password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            "autocomplete": "off",
            "class": "form-control",
            "type": "password",
            "placeholder": "Re Password",
        }
    ), min_length=6)


class LoginForm(forms.Form):
    email = forms.CharField(widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Email", "type": "email"}
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            "autocomplete": "off",
            "class": "form-control",
            "placeholder": "Password",
            "type": "password",
        }
    ), min_length=6)


class LostPassForm(forms.Form):
    email = forms.CharField(widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Email", "type": "email"}
    ))
