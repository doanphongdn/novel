# Generated by Django 3.1.4 on 2021-01-06 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_service', '0007_auto_20210105_1702'),
    ]

    operations = [
        migrations.AddField(
            model_name='crawlcampaign',
            name='paging_stopped_by_item',
            field=models.CharField(blank=True, default='', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='crawlitemaction',
            name='action',
            field=models.CharField(choices=[('Reverse Chapter List', 'Reverse Chapter List'), ('Format Chapter Content', 'Format Chapter Content'), ('Group Items', 'Group Items')], max_length=250),
        ),
    ]