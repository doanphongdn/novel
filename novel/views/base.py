import os

from django.views.generic import TemplateView


class NovelBaseView(TemplateView):
    def __init__(self, *args, **kwargs):
        # self.template_name = "novel/%s/%s" % (os.environ.get('TEMPLATE_BASE_USE', 'template1'), self.template_name)
        super().__init__(*args, **kwargs)
