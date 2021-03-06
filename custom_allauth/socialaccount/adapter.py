from allauth.account.utils import user_email
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount

from novel.models import NovelUserProfile
from novel.views.user import UserAction


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        NovelUserProfile(user_id=user.id, avatar=sociallogin.account.get_avatar_url()).save()
        UserAction.sync_histories(request, user)
        return user

    def pre_social_login(self, request, sociallogin):
        social_account = SocialAccount.objects.filter(uid=user_email(sociallogin.user)).first()
        if social_account:
            social_account.uid = sociallogin.account.uid
            social_account.extra_data = sociallogin.account.extra_data
            social_account.save()
            sociallogin.account = social_account
            sociallogin.user = social_account.user

        # Sync history to user after login success
        if sociallogin.user:
            UserAction.sync_histories(request, sociallogin.user)

        super().pre_social_login(request, sociallogin)


