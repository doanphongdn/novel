# Generated by Django 3.1.5 on 2021-01-24 21:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('novel', '0025_auto_20210124_2136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='novelsetting',
            name='meta_og_type',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
