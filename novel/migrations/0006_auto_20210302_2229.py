# Generated by Django 3.1.6 on 2021-03-02 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('novel', '0005_novelreport'),
    ]

    operations = [
        migrations.AddField(
            model_name='genre',
            name='style_color',
            field=models.CharField(blank=True, default='', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='novelreport',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
