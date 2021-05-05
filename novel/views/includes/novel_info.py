from django.contrib.auth.models import AnonymousUser

from novel.models import Bookmark
from novel.views.includes.base import BaseTemplateInclude


class NovelInfoTemplateInclude(BaseTemplateInclude):
    name = "novel_info"
    template = "novel/includes/novel_info.html"

    @staticmethod
    def get_bookmark_info(novel_id, user):
        is_logged = not isinstance(user, AnonymousUser)
        bmk_count = Bookmark.objects.filter(novel_id=novel_id).count()
        bookmark_info = {
            "status": "nofollow",
            "text": ("%s %s" % (bmk_count or "", "Bookmark")).strip(),
            "is_logged": is_logged,
        }
        if is_logged:
            bmk_count = Bookmark.objects.filter(novel_id=novel_id, user_id=user.id).count()
            if bmk_count > 0:
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
