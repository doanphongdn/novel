from novel.form.user import UserProfileForm
from novel.views.base import NovelBaseView


class UserProfileView(NovelBaseView):
    template_name = "novel/user.html"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        user_info = {
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
            "user": request.user.username,
        }
        setting_form = UserProfileForm(initial=user_info)
        kwargs["setting_form"] = setting_form

        extra_data = {
            'user_profile': {
                'setting_form': setting_form,
                'user': request.user
            }
        }
        user_profile = self.incl_manager.render_include_html('user', extra_data=extra_data, request=request)
        response.context_data.update({
            "user_profile_html": user_profile
        })

        return response
