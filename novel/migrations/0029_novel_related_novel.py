# Generated by Django 3.1.12 on 2021-07-03 18:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('novel', '0028_auto_20210603_1434'),
    ]

    operations = [
        migrations.AddField(
            model_name='novel',
            name='related_novel',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='novel.novel'),
        ),
    ]