from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from novel.models import NovelUserProfile
from novel.views.user import UserAction


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        NovelUserProfile(user_id=user.id, avatar=sociallogin.account.get_avatar_url()).save()
        return user

    def pre_social_login(self, request, sociallogin):
        # Sync history to user after login success
        UserAction.sync_histories(request, sociallogin.user)
        super().pre_social_login(request, sociallogin)


