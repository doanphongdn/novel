# Generated by Django 3.1.4 on 2020-12-25 03:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_service', '0006_auto_20201224_1719'),
    ]

    operations = [
        migrations.AddField(
            model_name='crawlcampaign',
            name='last_run',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='crawlcampaign',
            name='repeat_time',
            field=models.IntegerField(default=5, help_text='Minutes to repeat this campaign'),
        ),
        migrations.AddField(
            model_name='crawlcampaign',
            name='status',
            field=models.CharField(choices=[('running', 'Running'), ('stopped', 'Stopped')], default='stopped', max_length=10),
            preserve_default=False,
        ),
    ]
