from django_cms import settings
from novel.form.auth import LoginForm, RegisterForm, LostPassForm
from novel.views.includes.base import BaseTemplateInclude


class BaseAuthModalTemplateInclude(BaseTemplateInclude):
    cache = False
    name = "base_auth_modal"
    template = "novel/includes/base_auth_modal.html"

    def prepare_include_data(self):
        super().prepare_include_data()
        login_form = LoginForm()
        register_form = RegisterForm()
        lost_pass_form = LostPassForm()

        self.include_data.update({
            "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_SITE_KEY,
            "login_form": login_form,
            "register_form": register_form,
            "lost_pass_form": lost_pass_form,
        })
