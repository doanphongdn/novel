import json
from http import HTTPStatus

from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import User, AnonymousUser
from django.db import transaction
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404

from novel.form.auth import RegisterForm, LoginForm
from novel.form.user import UserProfileForm
from novel.models import Novel, Bookmark, History, NovelChapter
from novel.utils import get_history_cookies
from novel.views.base import NovelBaseView
from novel.views.includes.novel_info import NovelInfoTemplateInclude


class UserAction(object):

    @classmethod
    def storage_history(cls, user, chapter_ids):
        if isinstance(user, AnonymousUser):
            return

        if not isinstance(chapter_ids, list):
            chapter_ids = [chapter_ids]

        values = NovelChapter.objects.filter(id__in=chapter_ids).values_list("id", "novel_id")
        history_update_objs = []
        history_create_objs = []
        for val in values:
            history = History.objects.filter(user=user, novel_id=val[1]).first()
            if history:
                history.chapter_id = val[0]
                history_update_objs.append(history)
            else:
                history_create_objs.append(History(user=user, chapter_id=val[0], novel_id=val[1]))

        if history_create_objs:
            History.objects.bulk_create(history_create_objs, ignore_conflicts=True)

        if history_update_objs:
            History.objects.bulk_update(history_update_objs, ['chapter_id'])

    @classmethod
    def sync_histories(cls, request, user=None):
        if not user:
            user = request.user

        if isinstance(user, AnonymousUser):
            return

        histories = get_history_cookies(request)
        cls.storage_history(user, list(histories.values()))

    @staticmethod
    def bookmark(request):
        if request.method == 'POST':
            novel_id = request.POST.get('novel_id')
            status = request.POST.get('status')
            if not novel_id:
                return JsonResponse({
                    "success": False,
                    "message": "No novels found",
                })

            try:
                with transaction.atomic():
                    novel = get_object_or_404(Novel, id=int(novel_id))
                    if not isinstance(request.user, AnonymousUser):
                        if status == 'nofollow':
                            bmk, created = Bookmark.objects.get_or_create(user_id=request.user.id, novel=novel)
                            if created:
                                novel.follow += 1
                                novel.save()

                        elif status == "followed":
                            bmk = Bookmark.objects.filter(user_id=request.user.id, novel=novel).first()
                            if bmk:
                                bmk.delete()
                                novel.follow -= 1
                                novel.save()

                return JsonResponse({
                    "success": True,
                    "message": "Success",
                    "bookmark_info": NovelInfoTemplateInclude.get_bookmark_info(novel_id, request.user)
                }, status=HTTPStatus.OK)

            except Exception as ex:
                return JsonResponse({
                    "success": False,
                    "message": repr(ex),
                }, status=HTTPStatus.BAD_REQUEST)

        return JsonResponse({}, status=HTTPStatus.BAD_REQUEST)

    @staticmethod
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

    @staticmethod
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

        # request.session.set_expiry(0)
        login(request, user)

        # Sync histories from cookie
        UserAction.sync_histories(request, user)

        return JsonResponse({"success": True, "redirect_to": request.COOKIES.get('_redirect_url') or "/"})

    @staticmethod
    def user_logout(request):
        logout(request)
        redirect_url = request.COOKIES.get('_redirect_url') or "/"
        return HttpResponseRedirect(redirect_url)


class UserProfileView(NovelBaseView):
    template_name = "novel/user.html"

    __no_require_logged = ("history",)
    __require_logged = ("overview", "message", "comment", "bookmark")

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        tab_name = kwargs.get("tab_name")
        full_tab = self.__no_require_logged + self.__require_logged

        if (self.is_logged and tab_name not in full_tab) or (
                not self.is_logged and tab_name not in self.__no_require_logged):
            return HttpResponseRedirect("/")

        extra_data = {
            'user_profile': {
                "page": request.GET.get('page') or 1,
                'user': request.user,
                'view_type': request.GET.get('view') or 'grid',
                'tab_name': tab_name,
                'is_logged': self.is_logged
            }
        }

        if self.is_logged:
            extra_data['user_profile'].update({
                'setting_form': UserProfileForm(
                    initial={
                        "first_name": request.user.first_name,
                        "last_name": request.user.last_name,
                        "email": request.user.email,
                        "user": request.user.username,
                    }),
                'tab_enabled': full_tab,
            })

        user_profile = self.incl_manager.render_include_html('user', extra_data=extra_data,
                                                             request=request, request_param_code=tab_name)
        response.context_data.update({
            "user_profile_html": user_profile,
        })

        return response
