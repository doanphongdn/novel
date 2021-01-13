from cms.models import FooterInfo, Link
from novel.views.includes.base import BaseTemplateInclude
from novel.views.includes.link import LinkTemplateInclude


class FooterTemplateInclude(BaseTemplateInclude):
    template = "novel/includes/footer.html"

    def __init__(self):
        super().__init__()

        footer_info = FooterInfo.objects.filter(active=1).first()
        if footer_info:
            default_footer_info = False
        else:
            default_footer_info = True

        tags = Link.objects.filter(type='hashtag', active=1).all()
        if tags:
            hashtag = LinkTemplateInclude(**{"link_data": tags, 'link_label': 'Hashtag'})
        else:
            hashtag = None

        self.include_data = {
            "footer_info": footer_info,
            "default_footer_info": default_footer_info,
            "link_html": hashtag.render_html() if hashtag else '',
        }
