# Generated by Django 5.1.1 on 2024-11-18 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=100)),
                ('units', models.PositiveIntegerField()),
                ('semester', models.CharField(max_length=50)),
                ('academic_year', models.CharField(max_length=50)),
                ('department', models.CharField(blank=True, max_length=100, null=True)),
                ('course_type', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
