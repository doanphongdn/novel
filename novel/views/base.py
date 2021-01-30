from hashlib import md5

from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.views.generic import TemplateView

from cms.include_mapping import IncludeMapping
from cms.models import TemplateManager
from novel.models import NovelSetting
from novel.views.includes.base_auth_modal import BaseAuthModalTemplateInclude
from novel.views.includes.base_navbar_menu import BaseNavbarTemplateInclude
from novel.views.includes.breadcrumb import BreadCrumbTemplateInclude
from novel.views.includes.chapter_content import ChapterContentTemplateInclude
from novel.views.includes.chapter_list import ChapterListTemplateInclude
from novel.views.includes.base_footer_info import FooterInfoplateInclude
from novel.views.includes.link import LinkTemplateInclude
from novel.views.includes.base_top_menu import TopMenuTemplateInclude
from novel.views.includes.novel_cat import NovelCatTemplateInclude
from novel.views.includes.novel_info import NovelInfoTemplateInclude
from novel.views.includes.novel_list import NovelListTemplateInclude
from novel.views.includes.pagination import PaginationTemplateInclude

TEMPLATE_INCLUDE_MAPPING = {
    "chapter_content": ChapterContentTemplateInclude,
    "chapter_list": ChapterListTemplateInclude,
    "link": LinkTemplateInclude,
    "novel_genres": NovelCatTemplateInclude,
    "novel_info": NovelInfoTemplateInclude,
    "novel_list": NovelListTemplateInclude,
    "breadcrumb": BreadCrumbTemplateInclude,
    "pagination": PaginationTemplateInclude,
    "base_footer_info": FooterInfoplateInclude,
    "base_top_menu": TopMenuTemplateInclude,
    "base_navbar_menu": BaseNavbarTemplateInclude,
    "base_auth_modal": BaseAuthModalTemplateInclude,
}


class NovelBaseView(TemplateView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.include_mapping = None

    def get(self, request, *args, **kwargs):
        request_url = request.build_absolute_uri()
        cache_key_md5 = md5(request_url.encode("utf-8")).hexdigest()
        novel_setting = cache.get(cache_key_md5)
        if not novel_setting:
            novel_setting = NovelSetting.get_setting()
            cache.set(cache_key_md5, novel_setting)

        # define list of include template class
        self.include_mapping = IncludeMapping(TEMPLATE_INCLUDE_MAPPING, cache_key_md5)

        title = ""
        logo = ""
        favicon = ""
        img_view = ""
        domain = ""
        meta_og_url = ""
        meta_og_type = ""
        meta_og_title = ""
        meta_og_description = ""
        meta_fb_app_id = ""
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

        base_footer_tmpl = TemplateManager.objects.filter(page_file='base_footer').first()
        base_other_html_tmpl = TemplateManager.objects.filter(page_file='base_other_html').first()
        base_navbar_tmpl = TemplateManager.objects.filter(page_file='base_navbar').first()
        base_top_menu_tmpl = TemplateManager.objects.filter(page_file='base_top_menu').first()

        kwargs["base_footer_html"] = self.include_mapping.render_include_html(base_footer_tmpl)
        kwargs["base_other_html"] = self.include_mapping.render_include_html(base_other_html_tmpl)
        kwargs["base_top_menu_html"] = self.include_mapping.render_include_html(base_top_menu_tmpl)
        kwargs["base_navbar_menu_html"] = self.include_mapping.render_include_html(base_navbar_tmpl)

        return super().get(request, *args, **kwargs)
