LOGIN_REDIRECT_URL = '/'
SOCIALACCOUNT_ADAPTER = 'custom_allauth.socialaccount.adapter.CustomSocialAccountAdapter'
ACCOUNT_ADAPTER = 'custom_allauth.account.adapter.CustomAccountAdapter'

AUTHENTICATION_BACKENDS = [
    # # Needed to login by username in Django admin, regardless of `allauth`
    # 'django.contrib.auth.backends.ModelBackend',
    # # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'LOCALE_FUNC': lambda request: 'en_US',
    },
    'zalo': {
        'SCOPE': [
            'access_profile',
        ],
        'LOCALE_FUNC': lambda request: 'en_US',
    },
    'facebook': {
        'METHOD': 'oauth2',
        'SDK_URL': '//connect.facebook.net/{locale}/sdk.js',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'first_name',
            'last_name',
            'middle_name',
            'name',
            'name_format',
            'picture',
            'short_name'
        ],
        'EXCHANGE_TOKEN': True,
        'LOCALE_FUNC': lambda request: 'en_US',
        'VERIFIED_EMAIL': False,
        'VERSION': 'v7.0',
    }
}
