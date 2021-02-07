from django.core.management.base import BaseCommand

from novel.models import Novel, NovelChapter, NovelFlat


class Command(BaseCommand):
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    def handle(self, *args, **kwargs):
        novels = Novel.objects.prefetch_related("novel_flat").all()
        for novel in novels:
            novel.update_flat_info()
            novel.save()
