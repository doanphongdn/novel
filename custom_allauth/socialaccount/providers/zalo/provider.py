from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class ZaloAccount(ProviderAccount):
    def get_avatar_url(self):
        return self.account.extra_data.get('picture', None)

    def to_str(self):
        dflt = super(ZaloAccount, self).to_str()
        return self.account.extra_data.get("name", dflt)


class ZaloProvider(OAuth2Provider):
    id = 'zalo'
    name = 'zalo'
    account_class = ZaloAccount

    def extract_uid(self, data):
        return str(data.get('id'))

    def extract_common_fields(self, data):
        return dict(name=data.get('name'))


providers.registry.register(ZaloProvider)
