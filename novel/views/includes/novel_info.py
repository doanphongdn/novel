from novel.views.includes.base import BaseTemplateInclude
from novel.views.includes.link import LinkTemplateInclude


class NovelInfoTemplateInclude(BaseTemplateInclude):
    name = "novel_info"
    template = "novel/includes/novel_info.html"

    def __init__(self, include_data, extra_data=None):
        super().__init__(include_data, extra_data)

        comment_enable = self.include_data.get("comment_enable")
        if comment_enable is None:
            comment_enable = True

        bookmark_enable = self.include_data.get("bookmark_enable")
        if bookmark_enable is None:
            bookmark_enable = True

        hashtags = LinkTemplateInclude(include_data={
            'link_type': self.include_data.get('hashtags_link_type'),
            'link_label': self.include_data.get('hashtags_link_label'),
        })

        self.include_data = {
            "novel": self.include_data.get("novel"),
            "author_label": self.include_data.get("author_label") or "Authors",
            "category_label": self.include_data.get("category_label") or "Categories",
            "latest_update_label": self.include_data.get("latest_update_label") or "Latest update",
            "chapter_total_label": self.include_data.get("chapter_total_label") or "Chapters",
            "view_total_label": self.include_data.get("view_total_label") or "Views",
            "status_label": self.include_data.get("view_total_label") or "Status",
            "first_chapter_label": self.include_data.get("first_chapter_label") or "First chap",
            "latest_chapter_label": self.include_data.get("latest_chapter_label") or "Latest chap",
            "issue_label": self.include_data.get("issue_label") or "Issue",
            "comment_label": self.include_data.get("comment_label") or "Comments",
            "bookmark_label": self.include_data.get("bookmark_label") or "Bookmark",
            "comment_enable": comment_enable,
            "bookmark_enable": bookmark_enable,
            "hashtags_html": hashtags.render_html(),
        }
