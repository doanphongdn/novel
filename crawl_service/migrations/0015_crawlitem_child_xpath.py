# Generated by Django 3.1.5 on 2021-01-20 01:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_service', '0014_auto_20210116_0537'),
    ]

    operations = [
        migrations.AddField(
            model_name='crawlitem',
            name='child_xpath',
            field=models.CharField(default='', help_text='Group all child item to one', max_length=250),
            preserve_default=False,
        ),
    ]