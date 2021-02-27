from django_cms import settings
from novel.form.report import ReportForm
from novel.views.includes.base import BaseTemplateInclude


class ReportModalTemplateInclude(BaseTemplateInclude):
    name = "report_modal"
    template = "novel/includes/report_modal.html"

    def prepare_include_data(self):
        super().prepare_include_data()

        chapter = self.include_data.get('chapter', None)
        novel = self.include_data.get('novel', None)
        if chapter:
            novel = chapter.novel

        report_form = ReportForm(initial={
            "novel_id": novel.id if novel else None,
            "chapter_id": chapter.id if chapter else None,
        })

        self.include_data.update({
            "recapcha_site_key": settings.GOOGLE_RECAPTCHA_SITE_KEY,
            "report_form": report_form,
            "novel_name": novel.name if novel else "",
            "chapter_name": chapter.name if chapter else "",
        })
