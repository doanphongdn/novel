from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from novel.models import NovelUserProfile


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        NovelUserProfile(user_id=user.id, avatar=sociallogin.account.get_avatar_url()).save()
        return user
