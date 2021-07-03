from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from novel.models import NovelNotify


class Command(BaseCommand):

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--days',
            dest='days',
            type=int,
            default=30
        )

    def handle(self, *args, **kwargs):
        __days = kwargs.get("days")
        limit_time = datetime.now() - timedelta(days=30)
        available_notify = NovelNotify.objects.filter(
            created_at__lte=limit_time
        ).all()
        if available_notify:
            available_notify.delete()
            print('[notify] deleted %s records' % len(available_notify))
