import requests
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)

from .client import ZaloOAuth2Client
from .provider import ZaloProvider


class ZaloOAuth2Adapter(OAuth2Adapter):
    client_class = ZaloOAuth2Client
    provider_id = ZaloProvider.id
    access_token_method = 'GET'
    access_token_url = 'https://oauth.zaloapp.com/v3/access_token'
    authorize_url = 'https://oauth.zaloapp.com/v3/permission'
    identity_url = 'https://graph.zalo.me/v2.0/me'

    supports_state = True

    def complete_login(self, request, app, token, **kwargs):
        extra_data = self.get_data(token.token)
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)

    def get_data(self, token):
        # Verify the user first
        resp = requests.get(
            self.identity_url,
            params={'access_token': token, "fields": "id,name,picture"}
        )

        if resp.status_code not in (200, 201):
            raise OAuth2Error()

        resp = resp.json()
        # Fill in their generic info
        info = {
            'name': resp.get('name'),
            'id': resp.get('id'),
            'picture': resp.get('picture', {}).get("data", {}).get("url", "")
        }

        return info


class ZaloOauth2LoginView(OAuth2LoginView):

    def get_client(self, request, app):
        return super().get_client(request, app)


oauth2_login = OAuth2LoginView.adapter_view(ZaloOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(ZaloOAuth2Adapter)
