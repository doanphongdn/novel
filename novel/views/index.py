from novel.views.base import NovelBaseView


class NovelIndexView(NovelBaseView):
    template_name = "novel/index.html"
    ads_group_name = "index"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        index_include_html = self.incl_manager.render_include_html('index', request=request)

        response.context_data.update({
            'index_include_html': index_include_html,
        })

        return response
