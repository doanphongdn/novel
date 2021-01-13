from django.shortcuts import redirect
from django.views.generic import TemplateView

from novel.models import NovelSetting
from novel.views.includes.footer import FooterTemplateInclude
from novel.views.includes.navbar import NavBarTemplateInclude


class NovelBaseView(TemplateView):

    def get(self, request, *args, **kwargs):
        novel_setting = NovelSetting.get_setting()
        title = ""
        logo = ""
        favicon = ""
        if novel_setting:
            title = novel_setting.title
            if novel_setting.logo:
                logo = novel_setting.logo.url
            if novel_setting.favicon:
                favicon = novel_setting.favicon.url

        menu = [
            {
                "url": "#",
                "name": "Facebook",
                "fa_icon": "fa fa-facebook-square",
            }
        ]
        navbar = NavBarTemplateInclude(menus=menu, title=title, logo=logo)
        footer = FooterTemplateInclude()

        kwargs["setting"] = {
            "title": title,
            "favicon": favicon,
            "meta_keywords": novel_setting and novel_setting.meta_keywords or "",
            "meta_description": novel_setting and novel_setting.meta_description or "",
            "meta_copyright": novel_setting and novel_setting.meta_copyright or "",
            "meta_author": novel_setting and novel_setting.meta_author or "",
            "google_analystics_id": novel_setting and novel_setting.google_analystics_id or "",
        }
        kwargs["navbar_html"] = navbar.render_html()
        kwargs["footer_html"] = footer.render_html()

        return super().get(request, *args, **kwargs)


def view_404(request, exception=None):
    # make a redirect to homepage
    # you can use the name of url or just the plain link
    return redirect('/') # or redirect('name-of-index-url')