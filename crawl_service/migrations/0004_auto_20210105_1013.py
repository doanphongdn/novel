# Generated by Django 3.1.4 on 2021-01-05 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_service', '0003_auto_20210104_1531'),
    ]

    operations = [
        migrations.AddField(
            model_name='crawlitem',
            name='multi',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='crawlitemaction',
            name='action',
            field=models.CharField(choices=[('Reverse', 'Reverse'), ('FormatChapterContent', 'FormatChapterContent')], max_length=250),
        ),
    ]
