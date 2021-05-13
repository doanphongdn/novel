import json
import logging
import os
from http import HTTPStatus

from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail, BadHeaderError
from django.db import transaction
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from sendgrid import Mail, SendGridAPIClient

from django_cms.utils.cache_manager import CacheManager
from novel import utils
from novel.form.auth import RegisterForm, LoginForm, LostPassForm
from novel.form.user import UserProfileForm
from novel.models import Novel, Bookmark, History, NovelChapter, NovelUserProfile, NovelNotify
from novel.utils import get_history_cookies
from novel.views.base import NovelBaseView
from novel.views.includes.novel_info import NovelInfoTemplateInclude
from django.utils.translation import gettext as _

logger = logging.getLogger('django')


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
    def novel_remove(request):
        res = JsonResponse({"success": False, })
        if request.method == 'POST':
            try:
                novel_id = request.POST.get('novel_id')
                action = request.POST.get('action')
                class_model = {
                    "history": History,
                    "bookmark": Bookmark,
                }
                if not novel_id or action not in class_model:
                    return res

                res = JsonResponse({"success": True, })
                if request.user and request.user.is_authenticated:
                    class_model.get(action).objects.filter(user=request.user, novel_id=novel_id).delete()
                elif action == "history":
                    cookies = utils.get_history_cookies(request)
                    cookies.pop(novel_id, None)
                    res.set_cookie("_histories", json.dumps(cookies))
            except:
                return res

        return res

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
    def read_notify(request):
        res = JsonResponse({"success": False, }, status=HTTPStatus.BAD_REQUEST)
        if request.method == 'POST':
            try:
                notify_id = request.POST.get('notify_id')
                notify = NovelNotify.objects.filter(id=notify_id).first()
                if notify:
                    notify.read = True
                    notify.save()
                    CacheManager(NovelNotify, **{"user_id": request.user.id, "read": False}).clear_cache()
                    CacheManager(NovelNotify, **{"user_id": request.user.id}).clear_cache()

                    res_data = {"success": True}
                    if notify.novel:
                        res_data["redirect_url"] = notify.novel.get_absolute_url()

                    res = JsonResponse(res_data, status=HTTPStatus.OK)
            except:
                pass

        return res

    @staticmethod
    def sign_up(request):
        register_form = RegisterForm(request.POST)
        if not register_form.is_valid():
            return JsonResponse({"success": False, "errors": register_form.errors})

        data = {key: value or None for key, value in request.POST.items() if hasattr(User, key)}
        data["username"] = data.get("email", '')
        data["last_name"] = request.POST.get("name", '')

        try:
            User.objects.create_user(**data)
        except Exception as ex:
            logger.error("[UserAction] ERROR: %s" % repr(ex))
            register_form.add_error("name",
                                    "Email này đã được đăng ký tài khoản. Vui lòng đăng nhập bằng google hoặc bấm quên mật khẩu để khôi phục lại.")
            return JsonResponse({"success": False, "errors": register_form.errors})

        try:
            user = authenticate(username=data.get("email", ''),
                                password=data.get("password", ''))
            request.session.set_expiry(0)
            login(request, user)
        except Exception as ex:
            logger.error("[UserAction] ERROR: %s" % repr(ex))
            register_form.add_error("name", "Tài khoản đã được tạo nhưng có lỗi khi đăng nhập, vui lòng thử lại sau.")
            return JsonResponse({"success": False, "errors": register_form.errors})

        return JsonResponse({"success": True})

    @staticmethod
    def password_reset_request(request):
        if request.method == "POST":
            password_reset_form = LostPassForm(request.POST)
            if password_reset_form.is_valid():
                data = password_reset_form.cleaned_data['email']
                user = User.objects.filter(email=data).first()
                if user:
                    domain = get_current_site(request).domain
                    subject = _("%s - Account password recovery request" % str(domain).capitalize())
                    email_template_name = "novel/password_reset/password_reset_email.html"
                    c = {
                        "email": user.email,
                        'domain': domain,
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'https',
                    }
                    html_content = render_to_string(email_template_name, c)
                    message = Mail(
                        from_email='noreply.nettruyen@gmail.com',
                        to_emails=user.email,
                        subject=subject,
                        html_content=html_content)
                    try:
                        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                        sg.send(message)
                    except Exception as ex:
                        return JsonResponse({"status": False,
                                             "message": _(
                                                 'Error sending password recovery email, please contact administrator')
                                             }, status=HTTPStatus.OK)

                    return JsonResponse({
                        "status": True, "message": _(
                            'Thank you for your request. '
                            'An email has been sent to you to verify your password recovery. '
                            'Please check your email and follow the instructions.')
                    }, status=HTTPStatus.OK)

        return JsonResponse({"status": False,
                             "message": _(
                                 'The email you provided does not exist in the system.')
                             }, status=HTTPStatus.OK)

    @staticmethod
    def redirect_url(request):
        redirect_url = request.COOKIES.get('_redirect_url') or "home"
        return HttpResponseRedirect(redirect_url)

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

    def post(self, request, *args, **kwargs):
        allow_url = reverse("user_profile", kwargs={"tab_name": "overview"})
        if request.path == allow_url and request.method == "POST" and request.user:
            form = UserProfileForm(request.POST)
            if form.is_valid():
                with transaction.atomic():
                    request.user.first_name = request.POST.get("first_name")
                    request.user.last_name = request.POST.get("last_name")
                    request.user.email = request.POST.get("email")

                    if request.POST.get("password"):
                        if request.POST.get("password") == request.POST.get("re_password"):
                            request.user.set_password(request.POST.get("password"))
                        else:
                            form.add_error("re_password", "Re password doesn't match.")
                            kwargs["profile_form"] = form
                            return self.get(request, *args, **kwargs)

                    avatar = request.FILES.get("avatar")
                    if avatar:
                        fs = FileSystemStorage()
                        filename = fs.save(avatar.name, avatar)
                        profile, _ = NovelUserProfile.objects.get_or_create(user_id=request.user.id)
                        profile.avatar = fs.url(filename)
                        profile.save()

                    request.user.save()

        return HttpResponseRedirect(request.path)

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        tab_name = kwargs.get("tab_name")
        profile_form = kwargs.get("profile_form")

        full_tab = self.__require_logged + self.__no_require_logged

        if (request.user.is_authenticated and tab_name not in full_tab) or (
                not request.user.is_authenticated and tab_name not in self.__no_require_logged):
            return HttpResponseRedirect("/")

        extra_data = {
            'user_profile': {
                "page": request.GET.get('page') or 1,
                'user': request.user,
                'view_type': request.GET.get('view') or 'grid',
                'tab_name': tab_name,
            }
        }

        if request.user.is_authenticated:
            extra_data['user_profile'].update({
                'profile_form': profile_form or UserProfileForm(
                    initial={
                        "first_name": request.user.first_name,
                        "last_name": request.user.last_name,
                        "email": request.user.email,
                        "user": request.user.username,
                    }),
                'tab_enabled': full_tab,
                'user_avatar': NovelUserProfile.get_avatar(request.user)
            })

        user_profile = self.incl_manager.render_include_html('user', extra_data=extra_data,
                                                             request=request, request_param_code=tab_name)
        response.context_data.update({
            "user_profile_html": user_profile,
        })

        return response
