# Generated by Django 3.1.5 on 2021-01-14 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_service', '0010_auto_20210111_1535'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='crawlcampaign',
            name='paging_param',
        ),
        migrations.AddField(
            model_name='crawlcampaign',
            name='next_page_xpath',
            field=models.CharField(blank=True, default='', help_text='Blank if no pagination.', max_length=250, null=True),
        ),
    ]