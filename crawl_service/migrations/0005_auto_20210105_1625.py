# Generated by Django 3.1.4 on 2021-01-05 16:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_service', '0004_auto_20210105_1013'),
    ]

    operations = [
        migrations.RenameField(
            model_name='crawlitem',
            old_name='parent_code',
            new_name='group_code',
        ),
        migrations.AlterUniqueTogether(
            name='crawlitem',
            unique_together={('campaign', 'code', 'group_code')},
        ),
    ]