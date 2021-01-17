# Generated by Django 3.1.5 on 2021-01-16 23:01

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0008_auto_20210116_1823'),
    ]

    operations = [
        migrations.AddField(
            model_name='templatemanager',
            name='properties',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='templatemanager',
            name='include_file',
            field=models.CharField(choices=[('chapter_list.html', 'chapter_list.html'), ('footer.html', 'footer.html'), ('novel_info.html', 'novel_info.html'), ('__breadcrumb.html', '__breadcrumb.html'), ('chapter_content.html', 'chapter_content.html'), ('novel_list.html', 'novel_list.html'), ('link.html', 'link.html'), ('__pagination.html', '__pagination.html'), ('__navbar.html', '__navbar.html')], max_length=250),
        ),
    ]