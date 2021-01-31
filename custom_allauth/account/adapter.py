from allauth.account.adapter import DefaultAccountAdapter

from custom_allauth import settings


class CustomAccountAdapter(DefaultAccountAdapter):

    def get_login_redirect_url(self, request):
        return settings.LOGIN_REDIRECT_URL
