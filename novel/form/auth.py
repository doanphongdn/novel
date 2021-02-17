from django import forms


class RegisterForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Name", "id": "register_name"}
    ), max_length=30)
    email = forms.CharField(widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Email", "type": "email", "id": "register_enail"}
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            "autocomplete": "off",
            "class": "form-control",
            "type": "password",
            "placeholder": "Password",
            "id": "register_password"
        }
    ), min_length=6)
    re_password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            "autocomplete": "off",
            "class": "form-control",
            "type": "password",
            "placeholder": "Re Password", "id": "register_re_password"
        }
    ), min_length=6)


class LoginForm(forms.Form):
    email = forms.CharField(widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Email", "type": "email", "id": "login_email"}
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            "autocomplete": "off",
            "class": "form-control",
            "placeholder": "Password",
            "type": "password",
            "id": "login_password"
        }
    ), min_length=6)


class LostPassForm(forms.Form):
    email = forms.CharField(widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Email", "type": "email", "id": "lost_pwd_email"}
    ))
