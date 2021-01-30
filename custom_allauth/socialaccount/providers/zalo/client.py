from urllib.parse import urlencode, quote, parse_qsl

import requests
from allauth.socialaccount.providers.oauth2.client import OAuth2Client, OAuth2Error


class ZaloOAuth2Client(OAuth2Client):
    """
    Custom client because `Sign In With Apple`:
        * requires `response_mode` field in redirect_url
        * requires special `client_secret` as JWT
    """

    def get_client_id(self):
        """ We support multiple client_ids, but use the first one for api calls """
        return self.consumer_key.split(",")[0]

    def get_redirect_url(self, authorization_url, extra_params):
        params = {
            "app_id": self.get_client_id(),
            "redirect_uri": self.callback_url,
            "response_mode": "form_post",
            "scope": self.scope,
            "response_type": "code id_token",
        }
        if self.state:
            params["state"] = self.state
        params.update(extra_params)
        return "%s?%s" % (authorization_url, urlencode(params, quote_via=quote))

    def get_access_token(self, code):
        params = {
            "redirect_uri": self.callback_url,
            "code": code,
            "app_id": self.consumer_key,
            "app_secret": self.consumer_secret,
        }
        self._strip_empty_keys(params)
        # TODO: Proper exception handling
        resp = requests.request(
            self.access_token_method,
            self.access_token_url,
            params=params,
            headers=self.headers,
        )

        access_token = None
        if resp.status_code in [200, 201]:
            # Weibo sends json via 'text/plain;charset=UTF-8'
            if (
                    resp.headers["content-type"].split(";")[0] == "application/json"
                    or resp.text[:2] == '{"'
            ):
                access_token = resp.json()
            else:
                access_token = dict(parse_qsl(resp.text))
        if not access_token or "access_token" not in access_token:
            raise OAuth2Error("Error retrieving access token: %s" % resp.content)
        return access_token
