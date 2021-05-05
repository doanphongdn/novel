import os
from concurrent.futures import ThreadPoolExecutor
import time

from django.core.management.base import BaseCommand

from django_cms import settings
from novel.models import NovelChapter
from novel.utils import get_first_number_pattern


class Command(BaseCommand):

    def update_chapter_name(self, chapter):
        if 'en' not in settings.LANGUAGE_CODE and chapter.name.startswith('Chapter'):
            chapter.name = chapter.name.replace('Chapter', os.environ.get('LANGUAGE_CHAPTER_NAME', 'Chương'))
            chapter.save()

    def handle(self, *args, **kwargs):
        print('[Chapter Replace Name] Starting...')
        num_chapters = 0
        while True:
            chapters = NovelChapter.objects.filter(active=True,
                                                   name__icontains='Chapter ').all()[0:25000]
            if not chapters:
                break
            start = time.perf_counter()  # start timer
            counter = len(chapters)
            with ThreadPoolExecutor(max_workers=3) as executor:
                results = executor.map(self.update_chapter_name,
                                       chapters)  # this is Similar to map(func, *iterables)
            finish = time.perf_counter()  # end timer

            print(f"[Chapter Replace Name] Finished update {counter} chapters "
                  f"in {round(finish - start, 2)} seconds")
            num_chapters += counter
            time.sleep(0.1)
        print(f"[Chapter Replace Name] Finished update total {num_chapters} chapters ")
