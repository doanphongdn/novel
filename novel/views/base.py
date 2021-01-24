from django.contrib.sites.shortcuts import get_current_site
from django.views.generic import TemplateView

from cms.include_mapping import IncludeMapping
from cms.models import TemplateManager
from novel.models import NovelSetting, Genre
from novel.views.includes.breadcrumb import BreadCrumbTemplateInclude
from novel.views.includes.chapter_content import ChapterContentTemplateInclude
from novel.views.includes.chapter_list import ChapterListTemplateInclude
from novel.views.includes.footer_info import FooterInfoplateInclude
from novel.views.includes.link import LinkTemplateInclude
from novel.views.includes.novel_info import NovelInfoTemplateInclude
from novel.views.includes.novel_list import NovelListTemplateInclude
from novel.views.includes.pagination import PaginationTemplateInclude
from novel.views.includes.novel_cat import NovelCatTemplateInclude
from novel.views.includes.menu import TopMenuTemplateInclude

TEMPLATE_INCLUDE_MAPPING = {
    "chapter_content": ChapterContentTemplateInclude,
    "chapter_list": ChapterListTemplateInclude,
    "link": LinkTemplateInclude,
    "novel_genres": NovelCatTemplateInclude,
    "novel_info": NovelInfoTemplateInclude,
    "novel_list": NovelListTemplateInclude,
    "breadcrumb": BreadCrumbTemplateInclude,
    "pagination": PaginationTemplateInclude,
    "footer_info": FooterInfoplateInclude,
    "menu": TopMenuTemplateInclude,
}


class NovelBaseView(TemplateView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.include_mapping = IncludeMapping(TEMPLATE_INCLUDE_MAPPING)

    def get(self, request, *args, **kwargs):
        novel_setting = NovelSetting.get_setting()
        title = ""
        logo = ""
        favicon = ""
        img_view = ""
        domain = ""
        if novel_setting:
            title = novel_setting.title
            current_site = get_current_site(request)
            domain = current_site.domain
            if 'http' not in domain:
                protocol = 'https' if request.is_secure() else 'http'
                domain = protocol + "://" + domain
            if novel_setting.logo:
                logo = novel_setting.logo.url
            if novel_setting.favicon:
                favicon = novel_setting.favicon.url
                img_view = domain + novel_setting.favicon.url

            # Other meta for facebook
            if novel_setting.meta_img:
                img_view = domain + novel_setting.meta_img.url
            meta_og_url = request.build_absolute_uri('?')
            meta_og_type = novel_setting.meta_og_type or "article"
            meta_og_title = title
            if novel_setting.meta_og_description:
                meta_og_description = novel_setting.meta_og_description
            else:
                meta_og_description = novel_setting.meta_description or ""
            meta_fb_app_id = novel_setting.meta_fb_app_id or None

        menu = [
            {
                "url": "#",
                "name": "Facebook",
                "fa_icon": "fa fa-facebook-square",
            }
        ]

        kwargs["setting"] = {
            "title": title,
            "domain": domain,
            "logo": logo,
            "favicon": favicon,
            "meta_keywords": novel_setting and novel_setting.meta_keywords or "",
            "meta_description": novel_setting and novel_setting.meta_description or "",
            "meta_copyright": novel_setting and novel_setting.meta_copyright or "",
            "meta_author": novel_setting and novel_setting.meta_author or "",
            "meta_og_url": meta_og_url,
            "meta_og_type": meta_og_type,
            "meta_og_title": meta_og_title,
            "meta_og_description": meta_og_description,
            "meta_fb_app_id": meta_fb_app_id,
            "meta_img": img_view,
            "google_analystics_id": novel_setting and novel_setting.google_analystics_id or "",
        }

        footer_tmpl = TemplateManager.objects.filter(page_file='footer').first()
        # navbar_tmpl = TemplateManager.objects.filter(page_file='navbar').first()

        top_menu_tmpl = TemplateManager.objects.filter(page_file='top_menu').first()

        kwargs["footer_html"] = self.include_mapping.render_include_html(footer_tmpl)
        kwargs["top_menu_html"] = self.include_mapping.render_include_html(top_menu_tmpl)

        return super().get(request, *args, **kwargs)
