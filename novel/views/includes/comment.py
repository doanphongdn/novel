from novel import settings
from novel.form.comment import CommentForm
from novel.views.includes.base import BaseTemplateInclude


class CommentTemplateInclude(BaseTemplateInclude):
    cache = False
    name = "comment"
    template = "novel/includes/comment.html"

    def prepare_include_data(self):
        super().prepare_include_data()

        comment_form = CommentForm()

        self.include_data.update({
            "recapcha_site_key": settings.GOOGLE_RECAPTCHA_SITE_KEY,
            "comment_form": comment_form
        })
