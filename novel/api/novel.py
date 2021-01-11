from rest_framework.response import Response
from rest_framework.views import APIView

from novel.models import Novel, NovelChapter


class APIViewNovelUpdateList(APIView):
    def get(self, request, *args, **kwargs):
        update_list = Novel.objects.filter(novel_updated=False, active=True).values_list('url', flat=True)
        return Response(update_list, status=200)


class APIViewNovelChapterUpdateList(APIView):
    def get(self, request, *args, **kwargs):
        update_list = NovelChapter.objects.filter(chapter_updated=False).values_list('url', flat=True). \
                          order_by("novel").order_by("-id")[0:5000]
        return Response(update_list, status=200)
