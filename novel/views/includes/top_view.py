from django_cms import settings
from django_cms.utils.cache_manager import CacheManager
from novel.cache_manager import NovelCache
from novel.form.auth import LoginForm, RegisterForm, LostPassForm
from novel.models import Novel
from novel.views.includes.base import BaseTemplateInclude


class TopViewTemplateInclude(BaseTemplateInclude):
    cache = False
    name = "top_view"
    template = "novel/includes/top_view.html"

    def prepare_include_data(self):
        super().prepare_include_data()
        novel_daily = NovelCache(Novel, limit=7, order_by=["-view_daily"]).get_from_cache(get_all=True)
        novel_monthly = NovelCache(Novel, limit=7, order_by=["-view_monthly"]).get_from_cache(get_all=True)
        novel_all = NovelCache(Novel, limit=7, order_by=["-view_total"]).get_from_cache(get_all=True)

        self.include_data.update({
            "novel_daily": novel_daily,
            "novel_monthly": novel_monthly,
            "novel_all": novel_all,
        })
