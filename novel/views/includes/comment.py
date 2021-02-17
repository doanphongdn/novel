import time
from copy import deepcopy
from http import HTTPStatus
from urllib.parse import urlencode

import requests
from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse, HttpResponse
from django.template import loader

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
                cmt = Comment.objects.create(**data)

                comment_item = CommentTemplateInclude.comment_item(cmt)
                comment_html = loader.render_to_string("novel/includes/comment_item.html", {"cmt_obj": comment_item})

                return JsonResponse({"success": True, "html": comment_html})

        return JsonResponse({"success": False})

    @staticmethod
    def get_comments(novel, page=1, limit_item=10):
        return CommentPaginator(novel, limit_item, page, parent_id__isnull=True)

    @staticmethod
    def comment_form(request, *args, **kwargs):
        init_data = {}
        comment_form = CommentForm()
        reply_id = request.POST.get("reply_id")
        parent_id = request.POST.get("parent_id")
        novel_id = request.POST.get("novel_id")
        chapter_id = request.POST.get("chapter_id")
        if request.user.is_authenticated:
            init_data["name"] = "%s %s" % (request.user.first_name, request.user.last_name)
            comment_form.fields['name'].widget.attrs.update({'readonly': True})

        comment_form.fields['content'].widget.attrs.update({'id': 'id_content_%s' % int(time.time())})
        comment_form.fields['name'].widget.attrs.update({'id': 'id_name_%s' % int(time.time())})
        comment_form.fields['novel_id'].widget.attrs.update({'id': 'id_novel_id_%s' % int(time.time())})
        comment_form.fields['parent_id'].widget.attrs.update({'id': 'id_parent_id_%s' % int(time.time())})
        comment_form.fields['chapter_id'].widget.attrs.update({'id': 'id_chapter_id_%s' % int(time.time())})
        comment_form.fields['reply_id'].widget.attrs.update({'id': 'id_reply_id_%s' % int(time.time())})

        init_data["parent_id"] = parent_id
        init_data["reply_id"] = reply_id
        init_data["novel_id"] = novel_id
        init_data["chapter_id"] = chapter_id
        comment_form.initial = init_data

        html = loader.render_to_string("novel/includes/comment_form.html",
                                       {'comment_form': comment_form, "comment_type_class": "comment-reply-form"},
                                       request=request)

        return JsonResponse({'html': html}, status=HTTPStatus.OK)


class CommentTemplateInclude(BaseTemplateInclude):
    cache = False
    name = "comment"
    template = "novel/includes/comment.html"

    @classmethod
    def comment_item(cls, comment):
        reply_to = ""
        if comment.reply_id:
            reply = Comment.objects.prefetch_related('user').get(pk=comment.parent_id)
            if reply:
                reply_to = reply.name
        user_id = comment.user.id if comment.user else None
        return {
            "comment": comment,
            "avatar": NovelUserProfile.get_avatar(user_id),
            "child_class": "child" if comment.parent_id else "",
            "user_type": "Mem" if comment.user else "Guest",
            "user_type_color": "#3f9d87" if comment.user else "#999",
            "reply_to": reply_to,

        }

    def prepare_include_data(self):
        super().prepare_include_data()
        comment_form = CommentForm()
        novel = self.include_data.get("novel")
        chapter = self.include_data.get("chapter")
        cke_novel_id = self.include_data.get("cke_novel_id")

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

        if cke_novel_id:
            comment_form.fields['content'].widget.attrs.update({'id': cke_novel_id})

        comment_form.initial = init_data

        comment_data = []
        for cmt in comments:
            comment_data.append(self.comment_item(cmt))

        self.include_data.update({
            "comment_form": comment_form,
            "comment_form_media": comment_form.media,
            "comment_data": comment_data,
            "comment_type_class": "comment-form",
        })
