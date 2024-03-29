# Generated by Django 3.1.7 on 2021-03-12 22:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('novel', '0011_auto_20210311_0127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='noveladvertisementplace',
            name='code',
            field=models.CharField(choices=[('base_header', 'BASE HEADER'), ('base_top', 'BASE TOP'), ('base_bottom', 'BASE BOTTOM'), ('base_scroll_left', 'BASE SCROLL LEFT'), ('base_scroll_right', 'BASE SCROLL RIGHT'), ('index_header', 'INDEX HEADER'), ('index_top', 'INDEX TOP'), ('index_bottom', 'INDEX BOTTOM'), ('index_sidebar', 'INDEX SIDEBAR'), ('novel_all_header', 'NOVEL ALL HEADER'), ('novel_all_top', 'NOVEL ALL TOP'), ('novel_all_end', 'NOVEL ALL END'), ('novel_info_header', 'NOVEL INFO HEADER'), ('novel_info_top', 'NOVEL INFO TOP'), ('novel_info_right', 'NOVEL INFO RIGHT'), ('novel_info_before_chap_list', 'NOVEL INFO BEFORE CHAP LIST'), ('novel_info_after_chap_list', 'NOVEL INFO AFTER CHAP LIST'), ('novel_info_before_comment', 'NOVEL INFO BEFORE COMMENT'), ('novel_chapter_header', 'NOVEL CHAPTER HEADER'), ('novel_chapter_top', 'NOVEL CHAPTER TOP'), ('novel_chapter_before_content', 'NOVEL CHPATER BEFORE IMAGE'), ('novel_chapter_inside_content', 'NOVEL CHPATER INSIDE IMAGE'), ('novel_chapter_before_comment', 'NOVEL CHPATER BEFORE COMMENT')], max_length=50, unique=True),
        ),
    ]
