# Generated by Django 3.1.6 on 2021-02-20 11:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0024_menu_extra_class'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='menu',
            unique_together={('name', 'type')},
        ),
    ]