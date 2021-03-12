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


class SidebarTemplateInclude(BaseTemplateInclude):
    name = "sidebar"
    template = "novel/includes/sidebar.html"
