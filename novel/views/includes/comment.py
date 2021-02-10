import time
from urllib.parse import urlencode

import requests
from django import forms
from django.contrib.auth.models import AnonymousUser
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.templatetags.static import static

from novel import settings
from novel.form.comment import CommentForm
from novel.models import Comment, NovelUserProfile
from novel.paginator import CommentPaginator
from novel.views.includes.base import BaseTemplateInclude


class CommentManager(object):
    @staticmethod
    def comment(request, *args, **kwargs):
        if request.method == 'POST':
            form = CommentForm(request.POST)
            if not form.is_valid():
                return JsonResponse({"success": False, "errors": form.errors})

            ''' Begin reCAPTCHA validation '''
            recaptcha_response = request.POST.get('g-recaptcha-response')
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            response = requests.get(url, urlencode(values))
            response = response.json()
            ''' End reCAPTCHA validation '''

            if response['success']:
                data = {key: value or None for key, value in request.POST.items() if hasattr(Comment, key)}
                data["user"] = None if isinstance(request.user, AnonymousUser) else request.user
                Comment(**data).save()

                return JsonResponse({"success": True})

        return JsonResponse({"success": False})

    @staticmethod
    def get_comments(novel, page=1, limit_item=10):
        return CommentPaginator(novel, limit_item, page, parent_id__isnull=True)


class CommentTemplateInclude(BaseTemplateInclude):
    cache = False
    name = "comment"
    template = "novel/includes/comment.html"

    def prepare_include_data(self):
        super().prepare_include_data()
        comment_form = CommentForm()
        novel = self.include_data.get("novel")
        chapter = self.include_data.get("chapter")

        init_data = {}
        comments = []
        if novel:
            init_data["novel_id"] = novel.id
            comments = CommentManager.get_comments(novel)

        if chapter:
            init_data["chapter_id"] = chapter.id

        if self.request.user.is_authenticated:
            init_data["name"] = "%s %s" % (self.request.user.first_name, self.request.user.last_name)
            comment_form.fields['name'].widget.attrs.update({'readonly': True})

        comment_form.fields['content'].widget.attrs.update({'id': 'id_content_%s' % int(time.time())})
        comment_form.initial = init_data

        comment_data = []
        for cmt in comments:
            reply_to = ""
            if cmt.reply_id:
                reply = Comment.objects.prefetch_related('user').get(pk=cmt.parent_id)
                if reply:
                    reply_to = reply.name

            comment_data.append({
                "comment": cmt,
                "avatar": NovelUserProfile.get_avatar(cmt.user.id),
                "child_class": "child" if cmt.parent_id else "",
                "user_type": "Mem" if cmt.user else "Guest",
                "user_type_color": "#3f9d87" if cmt.user else "#999",
                "reply_to": reply_to,

            })

        self.include_data.update({
            "recapcha_site_key": settings.GOOGLE_RECAPTCHA_SITE_KEY,
            "comment_form": comment_form,
            "comment_data": comment_data
        })
