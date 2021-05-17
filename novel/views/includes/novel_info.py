from django.contrib.auth.models import AnonymousUser

from django_cms.utils.cache_manager import CacheManager
from novel.cache_manager import BookmarkCountCache
from novel.models import Bookmark
from novel.views.includes.base import BaseTemplateInclude


class NovelInfoTemplateInclude(BaseTemplateInclude):
    cache = False
    name = "novel_info"
    template = "novel/includes/novel_info.html"

    @staticmethod
    def get_bookmark_info(novel_id, user):
        is_logged = not isinstance(user, AnonymousUser)
        bmk_count = BookmarkCountCache(Bookmark, **{"novel_id": novel_id}).get_from_cache()
        bookmark_info = {
            "status": "nofollow",
            "text": ("%s %s" % (bmk_count or "", "Bookmark")).strip(),
            "is_logged": is_logged,
        }
        if is_logged:
            bmk_count = CacheManager(Bookmark, **{"novel_id": novel_id,
                                                  "user_id": user.id}).get_from_cache()
            if bmk_count:
                bookmark_info.update({
                    "status": "followed",
                    "text": "Followed",
                })

        return bookmark_info

    def prepare_include_data(self):
        novel = self.include_data.get('novel')
        meaning_emoji = self.include_data.get('meaning_emoji') or "❤️✅"

        self.include_data.update({
            "bookmark": self.get_bookmark_info(novel.id, self.request.user),
            "meaning_emoji": meaning_emoji,
        })
