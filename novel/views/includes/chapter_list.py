from unidecode import unidecode

from django_cms.utils.cache_manager import CacheManager
from django_cms.models import Link
from novel.views.includes.base import BaseTemplateInclude
from novel.views.includes.link import LinkTemplateInclude


class ChapterListTemplateInclude(BaseTemplateInclude):
    cache = False
    name = "chapter_list"
    template = "novel/includes/chapter_list.html"

    def prepare_include_data(self):
        novel = self.include_data.get("novel")
        hashtags_link_type = self.include_data.get('hashtags_link_type')
        hashtags_link_label = self.include_data.get('hashtags_link_label')

        link_conditions = {
            "type": hashtags_link_type,
            "active": True
        }

        link_objs = CacheManager(Link, **link_conditions).get_from_cache(get_all=True)
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
            'link_label': hashtags_link_label,
        })

        # chapter_list = []
        # if novel.novel_flat:
        #     chapter_list = novel.novel_flat.chapters.get("list")
        chapter_list = novel.chapters

        self.include_data.update({
            "chapter_list": chapter_list,
            "hashtags_html": hashtags.render_html(),
        })
