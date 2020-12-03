# Generated by Django 3.1.4 on 2020-12-03 09:07

import crawl_service.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_service', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='crawlitem',
            name='parent',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='crawlcampaign',
            name='code',
            field=models.CharField(max_length=50, validators=[crawl_service.models.code_validate]),
        ),
        migrations.AlterField(
            model_name='crawlitem',
            name='code',
            field=models.CharField(max_length=50, validators=[crawl_service.models.code_validate]),
        ),
        migrations.AlterField(
            model_name='crawlitem',
            name='xpath_property',
            field=models.CharField(blank=True, help_text='@src, @href, text, html ..., Blank if parent item.', max_length=50, null=True),
        ),
    ]
