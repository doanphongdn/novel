# Generated by Django 3.1.6 on 2021-02-08 23:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_service', '0020_auto_20210206_0010'),
    ]

    operations = [
        migrations.AddField(
            model_name='cdnserver',
            name='campaign_source',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='crawl_service.crawlcampaignsource'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cdnserver',
            name='friendly_alias_url',
            field=models.CharField(default='https://cdn.nettruyen.vn/file/nettruyen/', max_length=250),
        ),
    ]
