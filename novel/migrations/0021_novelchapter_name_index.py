# Generated by Django 3.1.7 on 2021-03-28 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('novel', '0020_novelparam_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='novelchapter',
            name='name_index',
            field=models.FloatField(db_index=True, null=True),
        ),
    ]
