from django.core.management.base import BaseCommand

from novel.models import Novel, NovelChapter, NovelFlat


class Command(BaseCommand):
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    def handle(self, *args, **kwargs):
        chunk_size = 100
        idx = 0
        while True:
            offset = idx * chunk_size
            novels = Novel.objects.prefetch_related("novel_flat").all()[offset:offset + chunk_size]
            if not novels:
                return

            for novel in novels:
                novel.update_flat_info()
                novel.save()

            idx += 1
