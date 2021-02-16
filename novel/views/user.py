from novel.form.auth import RegisterForm, LoginForm
from novel.form.user import UserProfileForm
from novel.views.base import NovelBaseView

from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect


def sign_up(request):
    register_form = RegisterForm(request.POST)
    if not register_form.is_valid():
        return JsonResponse({"success": False, "errors": register_form.errors})

    try:
        data = {key: value or None for key, value in request.POST.items() if hasattr(User, key)}
        data["username"] = data.get("email", '')
        data["first_name"] = request.POST.get("name", '')
        User.objects.create_user(**data)
        user = authenticate(username=data.get("email", ''),
                            password=data.get("password", ''))
        request.session.set_expiry(0)
        login(request, user)
    except Exception as ex:
        register_form.add_error("username", "Lỗi khi tạo tài khoản, liên hệ Administrator để được hỗ trợ")
        return JsonResponse({"success": False, "errors": register_form.errors})

    return JsonResponse({"success": True})


def sign_in(request):
    login_form = LoginForm(request.POST)
    if not login_form.is_valid():
        return JsonResponse({"success": False, "errors": login_form.errors})

    user = authenticate(username=request.POST.get("email", ''),
                        password=request.POST.get("password", ''))
    if not user or not user.is_active or user.is_superuser:
        login_form.add_error("email", "Tài khoản hoặc mật khẩu không chính xác")
        return JsonResponse({
            "success": False,
            "errors": login_form.errors
        })

    request.session.set_expiry(0)
    login(request, user)

    # Sync history
    # history.sync_history_with_user(request)

    res = JsonResponse({"success": True, "redirect_to": request.POST.get("redirect_to") or "/"})

    # clear cookie
    # res.delete_cookie('comic_history')

    return res


def user_logout(request):
    logout(request)
    return redirect('home')


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
