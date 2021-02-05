# Generated by Django 3.1.6 on 2021-02-06 00:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_service', '0019_cdnserver_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='cdnserver',
            name='friendly_url',
            field=models.CharField(default='https://f000.backblazeb2.com/file/nettruyen/', max_length=250),
        ),
        migrations.AddField(
            model_name='cdnserver',
            name='s3_url',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
