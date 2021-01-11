from django.templatetags.static import static
from django.views.generic import TemplateView

from novel.models import NovelSetting
from novel.views.includes.footer import FooterTemplateInclude
from novel.views.includes.navbar import NavBarTemplateInclude


class NovelBaseView(TemplateView):

    def get(self, request, *args, **kwargs):
        novel_setting = NovelSetting.get_setting()
        title = novel_setting and novel_setting.title or ""
        logo = novel_setting and novel_setting.logo.url or ""

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
            "favicon": novel_setting and novel_setting.favicon.url or "",
            "meta_keywords": novel_setting and novel_setting.meta_keywords or "",
            "meta_description": novel_setting and novel_setting.meta_description or "",
            "meta_copyright": novel_setting and novel_setting.meta_copyright or "",
            "meta_author": novel_setting and novel_setting.meta_author or "",
            "google_analystics_id": novel_setting and novel_setting.google_analystics_id or "",
        }
        kwargs["navbar_html"] = navbar.render_html()
        kwargs["footer_html"] = footer.render_html()

        return super().get(request, *args, **kwargs)
