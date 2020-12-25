# Generated by Django 3.1.4 on 2020-12-25 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('truyenhayho', '0009_auto_20201225_0419'),
    ]

    operations = [
        migrations.AddField(
            model_name='novelchapter',
            name='content',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='novelchapter',
            name='name',
            field=models.CharField(db_index=True, max_length=250),
        ),
    ]
