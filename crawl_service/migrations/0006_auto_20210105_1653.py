# Generated by Django 3.1.4 on 2021-01-05 16:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_service', '0005_auto_20210105_1625'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='crawlitem',
            unique_together={('campaign', 'code')},
        ),
        migrations.RemoveField(
            model_name='crawlitem',
            name='group_code',
        ),
    ]