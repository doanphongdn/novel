from allauth.account.adapter import DefaultAccountAdapter

from custom_allauth import settings


class CustomAccountAdapter(DefaultAccountAdapter):

    def get_login_redirect_url(self, request):
        return request.COOKIES.get('_redirect_url') or settings.LOGIN_REDIRECT_URL or "/"

