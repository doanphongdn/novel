# Generated by Django 3.1.5 on 2021-01-24 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0014_auto_20210124_1802'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inludetemplate',
            name='include_file',
            field=models.CharField(choices=[('chapter_content', 'chapter_content'), ('chapter_list', 'chapter_list'), ('link', 'link'), ('novel_info', 'novel_info'), ('novel_list', 'novel_list'), ('novel_genres', 'novel_cat'), ('breadcrumb', 'breadcrumb'), ('footer_info', 'footer_info'), ('menu', 'menu')], max_length=250),
        ),
        migrations.AlterField(
            model_name='templatemanager',
            name='page_file',
            field=models.CharField(choices=[('index', 'index'), ('chapter', 'chapter'), ('novel', 'novel'), ('novel_all', 'novel_all'), ('footer', 'footer'), ('navbar', 'navbar'), ('top_menu', 'top_menu')], max_length=250, unique=True),
        ),
    ]
