from novel.models import Novel, NovelChapter
from novel.views.base import NovelBaseView
from novel.views.includes.breadcrumb import BreadCrumbTemplateInclude
from novel.views.includes.chapter_content import ChapterContentTemplateInclude
from novel.views.includes.novel_info import NovelInfoTemplateInclude


class ChapterView(NovelBaseView):
    template_name = "novel/chapter.html"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        slug = kwargs.get('slug')
        chapter_slug = kwargs.get('chapter_slug')

        chapter = None
        breadcrumb_data = []
        novel = Novel.objects.filter(slug=slug).first()
        if novel:
            chapter = NovelChapter.objects.filter(slug=chapter_slug, novel=novel).first()
            if chapter:
                response.context_data["setting"]["title"] = novel.name + " " + chapter.name
                keywords = [novel.slug.replace('-', ' '), novel.name, novel.name + ' full',
                            chapter.slug.replace('-', ' '), chapter.name]
                response.context_data["setting"]["meta_keywords"] += ', ' + ', '.join(keywords)

            breadcrumb_data = [
                {
                    "name": novel.name,
                    "url": novel.get_absolute_url(),
                },
                {
                    "name": chapter.name,
                    "url": chapter.get_absolute_url(),
                }
            ]

        breadcrumb = BreadCrumbTemplateInclude(data=breadcrumb_data)
        chapter_content = ChapterContentTemplateInclude(chapter=chapter)

        response.context_data.update({
            'novel_url': novel.get_absolute_url(),
            'chapter_content_html': chapter_content.render_html(),
            'breadcrumb_html': breadcrumb.render_html(),
        })

        return response
