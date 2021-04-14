from django.contrib.sites.shortcuts import get_current_site
from django.template.context_processors import static
from django.views.generic import TemplateView

from django_cms import settings
from django_cms.utils.cache_manager import CacheManager
from django_cms.utils.include_mapping import IncludeManager
from novel.models import NovelSetting, NovelUserProfile, NovelAdvertisementPlace, NovelAdvertisement
from novel.views.includes.base_auth_modal import BaseAuthModalTemplateInclude
from novel.views.includes.base_footer_info import FooterInfotemplateInclude
from novel.views.includes.base_navbar_menu import BaseNavbarTemplateInclude
from novel.views.includes.base_top_menu import TopMenuTemplateInclude
from novel.views.includes.breadcrumb import BreadCrumbTemplateInclude
from novel.views.includes.chapter_content import ChapterContentTemplateInclude
from novel.views.includes.chapter_list import ChapterListTemplateInclude
from novel.views.includes.comment import CommentTemplateInclude
from novel.views.includes.link import LinkTemplateInclude
from novel.views.includes.novel_cat import NovelCatTemplateInclude
from novel.views.includes.novel_info import NovelInfoTemplateInclude
from novel.views.includes.novel_list import NovelListTemplateInclude
from novel.views.includes.pagination import PaginationTemplateInclude
from novel.views.includes.report_modal import ReportModalTemplateInclude
from novel.views.includes.sidebar import SidebarTemplateInclude
from novel.views.includes.user_profile import UserProfileTemplateInclude

TEMPLATE_INCLUDE_MAPPING = {
    "chapter_content": ChapterContentTemplateInclude,
    "chapter_list": ChapterListTemplateInclude,
    "link": LinkTemplateInclude,
    "novel_genres": NovelCatTemplateInclude,
    "novel_info": NovelInfoTemplateInclude,
    "novel_list": NovelListTemplateInclude,
    "breadcrumb": BreadCrumbTemplateInclude,
    "pagination": PaginationTemplateInclude,
    "base_footer_info": FooterInfotemplateInclude,
    "base_top_menu": TopMenuTemplateInclude,
    "base_navbar_menu": BaseNavbarTemplateInclude,
    "base_auth_modal": BaseAuthModalTemplateInclude,
    "user_profile": UserProfileTemplateInclude,
    "comment": CommentTemplateInclude,
    "report_modal": ReportModalTemplateInclude,
    "sidebar": SidebarTemplateInclude,
}


class NovelBaseView(TemplateView):
    ads_group_name = "base"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.incl_manager = IncludeManager(TEMPLATE_INCLUDE_MAPPING)
        self.base_setting = {}

    def get(self, request, *args, **kwargs):
        # Base content, using for all page
        base_context = {
            "user_avatar": NovelUserProfile.get_avatar(request.user)
        }

        # Set hash for each request to use cache
        self.incl_manager.set_request_hash(request)
        self.incl_manager.set_context(base_context)

        # Get novel setting from cache
        novel_setting = CacheManager(NovelSetting).get_from_cache()

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
            self.base_setting["domain"] = domain
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

        extra_data = {
            "base_navbar_menu": {
                "user": request.user,
                "user_avatar": base_context.get("user_avatar")
            }
        }

        base_navbar = self.incl_manager.render_include_html('base_navbar', extra_data=extra_data, request=request)
        kwargs["base_navbar"] = base_navbar
        kwargs["recaptcha_site_key"] = settings.GOOGLE_RECAPTCHA_SITE_KEY
        kwargs["css_style"] = settings.CSS_STYLE
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
            "google_analytics_id": novel_setting and novel_setting.google_analytics_id or "",
            "no_image_index": False,
        }
        kwargs["base_context"] = base_context
        tmpl_codes = ['base_footer', 'base_other_html', 'base_top_menu']
        tmpl_htmls = self.incl_manager.get_include_htmls(tmpl_codes, request=request)
        for page_tmpl_code, html in tmpl_htmls.items():
            kwargs[page_tmpl_code] = html

        device = 'pc' if request.user_agent.is_pc else 'mobile'
        ads_base_places = CacheManager(NovelAdvertisementPlace,
                                       **{'group': 'base'}).get_from_cache(get_all=True)
        ads_data = {}
        for place in ads_base_places:
            ads = CacheManager(NovelAdvertisement,
                               **{'places__code': place.code,
                                  'ad_type__in': ['all', device]}).get_from_cache(get_all=True)
            for ad in ads:
                if place.code not in ads_data:
                    ads_data[place.code] = []

                ads_data[place.code].append(ad)

        ads_other_places = CacheManager(NovelAdvertisementPlace,
                                        **{'group': self.ads_group_name}).get_from_cache(get_all=True)
        for place in ads_other_places:
            ads = CacheManager(NovelAdvertisement,
                               **{'places__code': place.code,
                                  'ad_type__in': ['all', device]}).get_from_cache(get_all=True)
            if not ads:
                continue

            place_code = place.code
            base_code = "base" + place_code.replace(self.ads_group_name, "")
            if base_code in ads_data or place.base_override:
                place_code = base_code
                ads_data[place_code] = []

            for ad in ads:
                if place_code not in ads_data:
                    ads_data[place_code] = []

                ads_data[place_code].append(ad)

        kwargs["ads_data"] = ads_data
        kwargs["ads_group_name"] = self.ads_group_name

        response = super().get(request, *args, **kwargs)
        response.set_cookie('_redirect_url', request.build_absolute_uri())
        if request.user.is_authenticated and request.COOKIES.get('_histories'):
            response.delete_cookie('_histories')

        return response
