# Generated by Django 3.1.5 on 2021-01-16 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('novel', '0011_auto_20210113_1809'),
    ]

    operations = [
        migrations.AlterField(
            model_name='novel',
            name='url',
            field=models.TextField(unique=True),
        ),
        migrations.AlterField(
            model_name='novelchapter',
            name='url',
            field=models.TextField(unique=True),
        ),
    ]