# Generated by Django 3.1.7 on 2021-03-14 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('novel', '0013_auto_20210313_1537'),
    ]

    operations = [
        migrations.AddField(
            model_name='novelsetting',
            name='ads_txt',
            field=models.TextField(blank=True, null=True),
        ),
    ]
