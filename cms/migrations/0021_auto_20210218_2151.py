# Generated by Django 3.1.6 on 2021-02-18 21:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0020_auto_20210210_1405'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pagetemplate',
            old_name='includes_default',
            new_name='params',
        ),
    ]
