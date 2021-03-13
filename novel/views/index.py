from novel.views.base import NovelBaseView


class NovelIndexView(NovelBaseView):
    template_name = "novel/index.html"
    ads_group_name = "index"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        ads_data = response.context_data.get("ads_data", {})
        extra_data = {
            "sidebar": {
                "index_sidebar": ads_data.get("index_sidebar"),
            },
            "novel_list": {
                "inside_content_ads": ads_data.get("index_inside_content"),
            },
        }
        index_include_html = self.incl_manager.render_include_html('index', request=request, extra_data=extra_data)

        response.context_data.update({
            'index_include_html': index_include_html,
        })

        return response
