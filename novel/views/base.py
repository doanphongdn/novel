from django.shortcuts import redirect
from django.views.generic import TemplateView

from cms.models import TemplateManager
from novel.models import NovelSetting
from novel.views.includes.__mapping import IncludeMapping


class NovelBaseView(TemplateView):

    def get(self, request, *args, **kwargs):
        novel_setting = NovelSetting.get_setting()
        title = ""
        logo = ""
        favicon = ""
        img_view = ""
        domain = ""
        if novel_setting:
            title = novel_setting.title
            domain = novel_setting.domain
            if novel_setting.logo:
                logo = novel_setting.logo.url
            if novel_setting.favicon:
                favicon = novel_setting.favicon.url
                img_view = domain + novel_setting.favicon.url
            if novel_setting.meta_img:
                img_view = domain + novel_setting.meta_img.url

        menu = [
            {
                "url": "#",
                "name": "Facebook",
                "fa_icon": "fa fa-facebook-square",
            }
        ]
        # navbar = NavBarTemplateInclude(menus=menu, title=title, logo=logo)
        # footer = FooterTemplateInclude()

        kwargs["setting"] = {
            "title": title,
            "domain": domain,
            "favicon": favicon,
            "meta_keywords": novel_setting and novel_setting.meta_keywords or "",
            "meta_description": novel_setting and novel_setting.meta_description or "",
            "meta_copyright": novel_setting and novel_setting.meta_copyright or "",
            "meta_author": novel_setting and novel_setting.meta_author or "",
            "meta_img": img_view,
            "google_analystics_id": novel_setting and novel_setting.google_analystics_id or "",
        }

        tmpl = TemplateManager.objects.filter(page_file='footer').first()
        kwargs["footer_html"] = IncludeMapping.render_include_html(tmpl)

        return super().get(request, *args, **kwargs)
