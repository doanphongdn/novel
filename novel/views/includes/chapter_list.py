from django.core.paginator import Paginator
from unidecode import unidecode

from cms.models import Link
from novel.paginator import ChapterPaginator
from novel.views.includes.base import BaseTemplateInclude
from novel.views.includes.link import LinkTemplateInclude
from novel.views.includes.pagination import PaginationTemplateInclude


class ChapterListTemplateInclude(BaseTemplateInclude):
    name = "chapter_list"
    template = "novel/includes/chapter_list.html"

    def __init__(self, include_data, extra_data=None):
        super().__init__(include_data, extra_data)
        limit = self.include_data.get("limit") or 30
        page = self.include_data.get("chap_page") or 1
        title = self.include_data.get("title")
        info_title = self.include_data.get("info_title")
        info_icon = self.include_data.get("info_icon")
        icon = self.include_data.get("icon")
        novel = self.include_data.get("novel")

        chapters = ChapterPaginator(limit, page, novel__id=novel.id, chapter_updated=True, active=True)

        link_objs = Link.objects.filter(type=self.include_data.get('hashtags_link_type'), active=True).all()
        link_data = {}
        for link in link_objs:
            for name in [novel.name, unidecode(novel.name)]:
                name1 = name + " " + link.name
                if name1 not in link_data:
                    link_data[name1] = {
                        "name": name1,
                        "url": novel.get_absolute_url(),
                        'class_name': link.class_name
                    }
                name2 = link.name + " " + name
                if name2 not in link_data:
                    link_data[name2] = {
                        "name": name2,
                        "url": novel.get_absolute_url(),
                        'class_name': link.class_name
                    }

        hashtags = LinkTemplateInclude(include_data={
            'link_data': list(link_data.values()),
            'link_label': self.include_data.get('hashtags_link_label'),
        })

        paging_data = {
            "paginated_data": chapters,
            "page_label": "chap-page"
        }
        pagination = PaginationTemplateInclude(paging_data)

        self.include_data = {
            "chapters": chapters,
            "title": title,
            "info_title": info_title,
            "info_icon": info_icon,
            "icon": icon,
            "pagination_html": pagination.render_html(),
            "hashtags_html": hashtags.render_html(),
        }
