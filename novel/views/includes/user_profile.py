from django.urls import reverse

from novel.models import Novel, Bookmark, History, NovelChapter
from novel.views.includes.base import BaseTemplateInclude
from novel.views.includes.novel_list import NovelListTemplateInclude


class UserProfileTemplateInclude(BaseTemplateInclude):
    cache = False
    name = "user_profile"
    template = "novel/includes/user_profile.html"

    def prepare_include_data(self):
        user = self.include_data.get("user")
        page = self.include_data.get("page")
        view_type = self.include_data.get("view_type")

        setting_form = self.include_data.get("setting_form", None)
        tab_name = self.include_data.pop("tab_name", "")
        tab_enabled = self.include_data.pop("tab_enabled", [])
        tab_config = self.include_data.pop("tab_config", {})

        profile_menus = [{
            "url": reverse("user_profile", kwargs={'tab_name': tab}),
            "active_class": "active" if tab == tab_name else "",
            "name": tab_config.get(tab, {}).get("menu_name", ""),
            "icon": tab_config.get(tab, {}).get("icon", ""),
        } for tab in tab_enabled]

        profile_html = ""
        if user:
            if tab_name in ["bookmark", "history"]:
                if tab_name == "bookmark":
                    novel_ids = Bookmark.objects.filter(user=user).values_list('novel_id', flat=True)

                # end is history
                else:
                    values = History.objects.filter(user=user).values_list("novel", "chapter")
                    chapter_ids = []
                    novel_ids = []
                    for val in values:
                        novel_ids.append(val[0])
                        chapter_ids.append(val[1])

                    chapters = NovelChapter.objects.select_related("novel").filter(id__in=chapter_ids).all()
                    history_chapters = {chap.novel.id: chap for chap in chapters}
                    self.include_data.update({"custom_chapters": history_chapters})

                self.include_data.update({
                    "filter_by": {"id__in": novel_ids},
                    "show_button_type": True,
                    "paginate_enable": True,
                    "view_type": view_type,
                    "page": page
                })
                novel_list_incl = NovelListTemplateInclude(self.include_data, request=self.request)
                profile_html = novel_list_incl.render_html()

        self.include_data.update({
            "profile_html": profile_html,
            "profile_menus": profile_menus,
            "setting_form": setting_form
        })
