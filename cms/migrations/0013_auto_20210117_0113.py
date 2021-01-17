# Generated by Django 3.1.5 on 2021-01-17 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0012_auto_20210117_0036'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inludetemplate',
            name='cols',
        ),
        migrations.AddField(
            model_name='inludetemplate',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='inludetemplate',
            name='class_name',
            field=models.CharField(default='', max_length=250),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='inludetemplate',
            name='include_file',
            field=models.CharField(choices=[('chapter_content', 'chapter_content'), ('chapter_list', 'chapter_list'), ('link', 'link'), ('novel_info', 'novel_info'), ('novel_list', 'novel_list'), ('footer', 'footer'), ('navbar', 'navbar')], max_length=250),
        ),
        migrations.AlterField(
            model_name='templatemanager',
            name='page_file',
            field=models.CharField(choices=[('infex', 'index'), ('chapter', 'chapter'), ('novel', 'novel'), ('novel_all', 'novel_all')], max_length=250),
        ),
    ]