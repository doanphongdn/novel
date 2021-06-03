import logging

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.contrib.auth.models import User, Group
from django.contrib.sites.admin import SiteAdmin
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class MyUserAdmin(UserAdmin):
    menu_icon = "ri-user-3-fill"


class MyUserGroupAdmin(GroupAdmin):
    menu_icon = "ri-team-fill"


class MySiteAdmin(SiteAdmin):
    menu_icon = "ri-terminal-window-fill"


class CustomAuthForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': _("Username")}))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', "placeholder": _("Password")}),
    )


admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.unregister(Site)

admin.site.register(Group, MyUserGroupAdmin)
admin.site.register(User, MyUserAdmin)
admin.site.register(Site, MySiteAdmin)

admin.site.login_form = CustomAuthForm
admin.site.login_form = CustomAuthForm
