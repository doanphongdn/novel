from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetCompleteView

from novel.views.base import NovelBaseView


class ResetPasswordConfirmView(PasswordResetConfirmView, NovelBaseView):
    template_name = "novel/password_reset/password_reset_confirm.html"


class ResetPasswordCompleteView(PasswordResetCompleteView, NovelBaseView):
    template_name = "novel/password_reset/password_reset_complete.html"
