import json
from urllib.parse import urlparse

from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from django.shortcuts import redirect

from django_cms import settings
from novel.cache_manager import NovelCache
from novel.models import NovelChapter, Novel
from novel.utils import get_history_cookies
from novel.views.base import NovelBaseView
from novel.views.user import UserAction


class ChapterView(NovelBaseView):
    template_name = "novel/chapter.html"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        slug = kwargs.get('slug')
        chapter_slug = kwargs.get('chapter_slug')
        breadcrumb_data = []

        novel = NovelCache(Novel, **{"slug": slug}).get_from_cache()
        if novel:
            # TODO: not yet apply cache
            chapter = NovelChapter.objects.filter(slug=chapter_slug, novel=novel).prefetch_related(
                'cdnnovelfile_set').first()
            if chapter:
                breadcrumb_data = [
                    {
                        "name": novel.name,
                        "url": novel.get_absolute_url(),
                    },
                    {
                        "name": chapter.name if chapter else '',
                        "url": chapter.get_absolute_url() if chapter else '',
                    }
                ]

                referer = urlparse(chapter.src_url)
                if novel.thumbnail_image.strip().startswith('//'):
                    referer_url = referer.scheme
                else:
                    referer_url = referer.scheme + "://"  # + referer.netloc

                response.context_data["setting"]["title"] = novel.name + " " + chapter.name
                response.context_data['setting']['meta_img'] = referer_url + novel.thumbnail_image
                keywords = [novel.slug.replace('-', ' '), novel.name, novel.name + ' full',
                            chapter.slug.replace('-', ' '), chapter.name]
                response.context_data["setting"]["meta_keywords"] += ', ' + ', '.join(keywords)

                # hard code to ionore index img google bot
                response.context_data["setting"]["no_image_index"] = True

                # Update view count
                chapter_id = chapter.id

                # Update reading histories
                if isinstance(request.user, AnonymousUser):
                    histories = get_history_cookies(request)

                    # Set cookies
                    if isinstance(histories, dict):
                        histories[str(novel.id)] = chapter_id
                        response.set_cookie('_histories', json.dumps(histories))
                    else:
                        response.set_cookie('_histories', "{}")

                else:
                    UserAction.storage_history(request.user, chapter_id)

                chapters_viewed = request.session.get("chapters_viewed") or []
                if chapter_id not in chapters_viewed:
                    with transaction.atomic():
                        chapter.view_total += 1
                        chapter.save()

                        novel.view_total += 1
                        novel.view_daily += 1
                        novel.view_monthly += 1
                        novel.save()

                        chapters_viewed.append(chapter_id)

                    request.session["chapters_viewed"] = chapters_viewed
                    # request.session.set_expiry(3600)


        else:
            # TODO: define 404 page
            # direct to homepage
            return redirect('/')  # or redirect('name-of-index-url')

        extra_data = {
            "breadcrumb": {
                "breadcrumb_data": breadcrumb_data,
            },
            "chapter_content": {
                "chapter": chapter,
                "novel": novel
            },
            "comment": {
                "novel": novel,
                # Dont change cke_id, it using in base.js
                "cke_novel_id": "cke_novel_id",
            },
            "report_modal": {
                "chapter": chapter
            }
        }

        include_html = self.incl_manager.render_include_html('chapter', extra_data=extra_data, request=request)
        domain = response.context_data.get("setting", {}).get("domain", "")
        response.context_data.update({
            "thumbnail_image": domain + novel.stream_thumbnail_image,
            'novel_url': novel.get_absolute_url(),
            'include_html': include_html,
            'request_url': request.build_absolute_uri(),
        })

        return response
