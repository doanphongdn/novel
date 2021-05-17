from django.core.management.base import BaseCommand

from novel.models import Novel


class Command(BaseCommand):

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--type',
            dest='type',
        )

    def handle(self, *args, **kwargs):
        __type = kwargs.get("type") or 'daily'
        if __type == 'daily':
            Novel.objects.update(**{
                "view_daily": 0,
            })
        elif __type == 'monthly':
            Novel.objects.update(**{
                "view_monthly": 0,
            })
