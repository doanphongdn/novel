# Generated by Django 3.1.5 on 2021-01-14 16:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_service', '0011_auto_20210114_1555'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='crawlcampaign',
            name='paging_stopped_by_item',
        ),
    ]
