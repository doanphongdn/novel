# Generated by Django 3.1.6 on 2021-02-17 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('novel', '0039_auto_20210217_1005'),
    ]

    operations = [
        migrations.AddField(
            model_name='novel',
            name='hot_novel',
            field=models.BooleanField(default=False),
        ),
    ]