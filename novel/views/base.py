from django.contrib.sites.shortcuts import get_current_site
from django.views.generic import TemplateView

from cms.include_mapping import IncludeMapping
from cms.models import TemplateManager
from novel.models import NovelSetting
from novel.views.includes.breadcrumb import BreadCrumbTemplateInclude
from novel.views.includes.chapter_content import ChapterContentTemplateInclude
from novel.views.includes.chapter_list import ChapterListTemplateInclude
from novel.views.includes.footer_info import FooterInfoplateInclude
from novel.views.includes.link import LinkTemplateInclude
from novel.views.includes.novel_info import NovelInfoTemplateInclude
from novel.views.includes.novel_list import NovelListTemplateInclude
from novel.views.includes.pagination import PaginationTemplateInclude


TEMPLATE_INCLUDE_MAPPING = {
    "chapter_content": ChapterContentTemplateInclude,
    "chapter_list": ChapterListTemplateInclude,
    "link": LinkTemplateInclude,
    "novel_info": NovelInfoTemplateInclude,
    "novel_list": NovelListTemplateInclude,
    "breadcrumb": BreadCrumbTemplateInclude,
    "pagination": PaginationTemplateInclude,
    "footer_info": FooterInfoplateInclude,
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
        if novel_setting:
            title = novel_setting.title
            current_site = get_current_site(request)
            domain = current_site.domain
            if 'http' not in domain:
                domain = "//" + domain
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

        kwargs["setting"] = {
            "title": title,
            "domain": current_site.domain,
            "logo": logo,
            "favicon": favicon,
            "meta_keywords": novel_setting and novel_setting.meta_keywords or "",
            "meta_description": novel_setting and novel_setting.meta_description or "",
            "meta_copyright": novel_setting and novel_setting.meta_copyright or "",
            "meta_author": novel_setting and novel_setting.meta_author or "",
            "meta_img": img_view,
            "google_analystics_id": novel_setting and novel_setting.google_analystics_id or "",
        }

        tmpl = TemplateManager.objects.filter(page_file='footer').first()
        kwargs["footer_html"] = self.include_mapping.render_include_html(tmpl)

        return super().get(request, *args, **kwargs)
