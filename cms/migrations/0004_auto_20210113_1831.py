# Generated by Django 3.1.5 on 2021-01-13 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0003_hashtag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hashtag',
            name='url',
            field=models.CharField(max_length=255, null=True),
        ),
    ]