# Generated by Django 3.1.6 on 2021-02-07 23:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('novel', '0033_auto_20210205_0255'),
    ]

    operations = [
        migrations.RenameField(
            model_name='novel',
            old_name='campaign_source',
            new_name='src_campaign',
        ),
        migrations.RenameField(
            model_name='novel',
            old_name='latest_chapter_url',
            new_name='src_latest_chapter_url',
        ),
        migrations.RenameField(
            model_name='novel',
            old_name='url',
            new_name='src_url',
        ),
        migrations.RenameField(
            model_name='novelchapter',
            old_name='url',
            new_name='src_url',
        ),
        migrations.AlterUniqueTogether(
            name='novelchapter',
            unique_together={('slug', 'novel'), ('src_url', 'novel'), ('name', 'novel')},
        ),
    ]