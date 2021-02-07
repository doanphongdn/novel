from django.db.models.signals import pre_save
from django.dispatch import receiver

from novel.models import Novel


@receiver(pre_save, sender=Novel)
def create_novel_flat(sender, **kwargs):
    print(sender)
