# Generated by Django 3.1.7 on 2021-03-13 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_cms', '0007_auto_20210312_0013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inludetemplate',
            name='include_file',
            field=models.CharField(choices=[('chapter_content', 'Chapter content'), ('chapter_list', 'Chapter list'), ('link', 'Links'), ('novel_info', 'Novel (Comic) detail'), ('novel_list', 'Novel (Comic) list - grid'), ('novel_genres', 'Novel (Comic) genres'), ('breadcrumb', 'Breadcrumb'), ('base_footer_info', 'Base footer info'), ('base_top_menu', 'Base top menu'), ('base_navbar_menu', 'Base navbar menu'), ('base_auth_modal', 'Base auth modal'), ('report_modal', 'Report modal'), ('user_profile', 'User profile'), ('comment', 'Comment'), ('sidebar', 'Sidebar')], max_length=250),
        ),
    ]
