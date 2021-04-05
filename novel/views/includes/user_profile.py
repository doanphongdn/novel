import json

from django.urls import reverse
from django.utils.safestring import mark_safe

from django_cms.utils.paginator import ModelPaginator
from novel.form.user import UserProfileForm
from novel.models import Novel, Bookmark, History, NovelChapter, NovelUserProfile, NovelNotify
from novel.paginator import NotifyPaginator
from novel.utils import get_history_cookies
from novel.views.includes.base import BaseTemplateInclude
from novel.views.includes.novel_list import NovelListTemplateInclude
from novel.views.includes.pagination import PaginationTemplateInclude


class UserProfileTemplateInclude(BaseTemplateInclude):
    cache = False
    name = "user_profile"
    template = "novel/includes/user_profile.html"

    def prepare_include_data(self):
        user = self.include_data.get("user")
        page = self.include_data.get("page")
        view_type = self.include_data.get("view_type")

        profile_form = self.include_data.get("profile_form", None)
        tab_name = self.include_data.pop("tab_name", "")
        tab_enabled = self.include_data.pop("tab_enabled", ())
        tab_config = self.include_data.pop("tab_config", {})
        input_labels = self.include_data.pop("input_labels", {})
        input_icons = self.include_data.pop("input_icons", {})

        profile_menus = [{
            "url": reverse("user_profile", kwargs={'tab_name': tab}),
            "active_class": "active" if tab == tab_name else "",
            "name": tab_config.get(tab, {}).get("menu_name", ""),
            "icon": tab_config.get(tab, {}).get("icon", ""),
        } for tab in tab_enabled]

        profile_html = ""
        if tab_name in ["bookmark", "history"]:
            novel_grid_col_lg = 3
            if tab_name == "bookmark":
                novel_ids = Bookmark.objects.filter(user=user).order_by('-updated_at') \
                    .values_list('novel_id', flat=True)

            # end is history
            else:
                # get data from logger
                if user.is_authenticated:
                    values = History.objects.filter(user=user).order_by('-updated_at').values_list("novel", "chapter")
                    chapter_ids = []
                    novel_ids = []
                    for val in values:
                        novel_ids.append(val[0])
                        chapter_ids.append(val[1])
                # get from cookies
                else:
                    novel_grid_col_lg = 2
                    # Get chapter ids from cookie
                    histories = get_history_cookies(self.request)
                    chapter_ids = list(histories.values())
                    novel_ids = list(histories.keys())

                chapters = NovelChapter.objects.select_related("novel").filter(id__in=chapter_ids).all()
                history_chapters = {chap.novel.id: chap for chap in chapters}
                self.include_data.update({"custom_chapters": history_chapters})

            self.include_data.update({
                "novel_grid_col_lg": novel_grid_col_lg,
                "filter_by": {"id__in": novel_ids},
                "show_button_type": True,
                "paginate_enable": True,
                "view_type": view_type,
                "page": page,
                "show_button_remove": True,
                "button_remove_type": tab_name,
            })
            novel_list_incl = NovelListTemplateInclude(self.include_data, request=self.request)
            profile_html = novel_list_incl.render_html()

        elif tab_name == "overview":
            if user.is_authenticated:
                profile_input_item = """
                    <div class="form-group">
                        <label for="{input_id}">{input_label}:</label>
                        <div class="input-group input-group-alternative">
                            <div class="input-group-prepend"><span class="input-group-text">
                                <i class="{input_icon}"></i></span></div>
                            {input}
                        </div>
                        {input_errors}
                    </div>
                """
                html_groups = ["""<div class="col-md-12 col-lg-8">"""]
                profile_form = profile_form or UserProfileForm(initial={
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                })
                for field in profile_form.visible_fields():
                    if field.name != 'avatar':
                        html_groups.append(profile_input_item.format(
                            input_id=field.auto_id,
                            input_label=input_labels.get(field.name) or field.label,
                            input_icon=input_icons.get(field.name) or '',
                            input=field,
                            input_errors=field.errors,
                        ))
                    else:
                        html_groups.append("""<div class="profile-userbuttons">
                            <label for="{input_id}" class="btn btn-secondary btn-sm" style="cursor:pointer;">
                            <i class="fa fa-image"></i> Change Avatar</label>{input}</div>"""
                                           .format(input=field, input_id=field.auto_id))

                html_groups.append("<hr style='margin:5px 0 10px 0 !important;'>")
                html_groups.append("""<button type="submit" class="btn btn-warning d-block ml-auto">
                    <i class="fa fa-save"></i> {submit_label}
                    </button></div>""".format(submit_label=input_labels.get("submit_label") or "Save"))
                profile_html = mark_safe("".join(html_groups))
        elif tab_name == "message":
            html_groups = ["""<table class="table table-striped table-sm table-hover">"""]
            notify = NotifyPaginator(10, page, **{"user": user}, order_by=["read", "-id"])

            for n in notify:
                bold_class = "" if n.read else "font-weight: 600;"
                html_groups.append("""<tr style="cursor: pointer;" class="notify-message" data-id="%s">
                                        <td style="width:200px;%s">
                                            <i class="fa fa-calendar"></i> %s
                                        </td>
                                        <td style="%s">%s</td>
                                    </tr>""" %
                                   (n.id, bold_class, n.created_at.strftime("%d/%m/%Y %H:%M"), bold_class, n.notify))

            html_groups.append("""</tr></table>""")
            profile_html = mark_safe("".join(html_groups))
            pagination = PaginationTemplateInclude({"paginated_data": notify, "page_label": "page"})
            profile_html += pagination.render_html()

        self.include_data.update({
            "profile_html": profile_html,
            "profile_menus": profile_menus,
        })
