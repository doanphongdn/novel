from django.core.management.base import BaseCommand

from novel.models import Novel, NovelChapter, NovelFlat


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        novels = Novel.objects.prefetch_related("novel_flat").all()
        for novel in novels:
            chapter_condition = {
                "novel_id": novel.id,
                "chapter_updated": True,
                "active": True
            }
            chapters = NovelChapter.objects.filter(**chapter_condition).order_by("id").all()
            if not chapters:
                continue

            chapter_total = len(chapters)
            latest_chapter = chapters[chapter_total - 1]
            first_chapter = chapters[0]
            latest_chapter = {
                "name": latest_chapter.name,
                "url": latest_chapter.get_absolute_url(),
                "created_at": first_chapter.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            first_chapter = {
                "name": first_chapter.name,
                "url": first_chapter.get_absolute_url(),
                "created_at": first_chapter.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            chapter_json = {
                "total": chapter_total,
                "list": []
            }
            for chap in chapters:
                chapter_json["list"].append({
                    "name": chap.name,
                    "url": chap.get_absolute_url(),
                    "created_at": chap.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                })
            if not novel.novel_flat:
                flat = NovelFlat(first_chapter=first_chapter,
                                 latest_chapter=latest_chapter,
                                 chapters=chapter_json)
                novel.novel_flat = flat
                flat.save()
                novel.save()
            else:
                novel.novel_flat.first_chapter = first_chapter
                novel.novel_flat.latest_chapter = latest_chapter
                novel.novel_flat.chapters = chapter_json
                novel.novel_flat.save()