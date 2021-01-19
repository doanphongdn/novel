# Generated by Django 3.1.5 on 2021-01-20 01:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_service', '0015_crawlitem_child_xpath'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crawlitem',
            name='child_xpath',
            field=models.CharField(blank=True, help_text='Group all child item to one', max_length=250, null=True),
        ),
    ]
