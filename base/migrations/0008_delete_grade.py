# Generated by Django 5.1.2 on 2024-11-19 17:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_alter_facultyprofile_options_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Grade',
        ),
    ]