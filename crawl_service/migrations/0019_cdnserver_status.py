# Generated by Django 3.1.5 on 2021-02-03 02:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_service', '0018_cdnserver'),
    ]

    operations = [
        migrations.AddField(
            model_name='cdnserver',
            name='status',
            field=models.CharField(choices=[('running', 'RUNNING'), ('stopped', 'STOPPED')], default='stopped', max_length=10),
        ),
    ]
