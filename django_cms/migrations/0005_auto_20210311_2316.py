# Generated by Django 3.1.7 on 2021-03-11 23:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_cms', '0004_auto_20210310_2216'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inludetemplate',
            name='full_width',
        ),
        migrations.AlterField(
            model_name='inludetemplate',
            name='class_name',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
