# Generated by Django 3.1.6 on 2021-02-03 22:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('novel', '0029_cdnnovelfile'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='novel',
            options={'ordering': ['-id']},
        ),
    ]