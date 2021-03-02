from allauth.account.utils import user_email
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount

from novel.models import NovelUserProfile
from novel.views.user import UserAction


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def save_user(self, request, sociallogin, form=None):
        social_account = SocialAccount.objects.filter(uid=user_email(sociallogin.user)).first()
        if social_account:
            user = social_account.user
        else:
            user = super().save_user(request, sociallogin, form)

        NovelUserProfile(user_id=user.id, avatar=sociallogin.account.get_avatar_url()).save()
        return user

    def pre_social_login(self, request, sociallogin):
        # Sync history to user after login success
        UserAction.sync_histories(request, sociallogin.user)
        super().pre_social_login(request, sociallogin)


