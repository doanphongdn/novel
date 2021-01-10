from django.templatetags.static import static
from django.views.generic import TemplateView

from novel.views.includes.footer import FooterTemplateInclude
from novel.views.includes.navbar import NavBarTemplateInclude


class NovelBaseView(TemplateView):

    def get(self, request, *args, **kwargs):
        menu = [
            {
                "url": "#",
                "name": "Facebook",
                "fa_icon": "fa fa-facebook-square",
            }
        ]
        navbar = NavBarTemplateInclude(menus=menu, title="Novel", logo=static('images/logo.png'))
        footer = FooterTemplateInclude()

        kwargs["navbar_html"] = navbar.render_html()
        kwargs["footer_html"] = footer.render_html()

        return super().get(request, *args, **kwargs)
