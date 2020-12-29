import os

from django.templatetags.static import static
from django.views.generic import TemplateView

from novel.widgets.navbar import NovelNavBarWidget


class NovelBaseView(TemplateView):

    def get(self, request, *args, **kwargs):
        menu = [
            {
                "url": "#",
                "name": "Facebook",
                "fa_icon": "fa fa-facebook-square",
            }
        ]
        navbar = NovelNavBarWidget(menus=menu, title="Novel", logo=static('images/logo.png'))
        kwargs["navbar"] = navbar
        return super().get(request, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
