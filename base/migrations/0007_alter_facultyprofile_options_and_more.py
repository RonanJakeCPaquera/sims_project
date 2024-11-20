# Generated by Django 5.1.2 on 2024-11-19 17:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_alter_course_code'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='facultyprofile',
            options={},
        ),
        migrations.RemoveField(
            model_name='facultyprofile',
            name='contact_number',
        ),
        migrations.RemoveField(
            model_name='facultyprofile',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='facultyprofile',
            name='updated_at',
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('midterm_grade', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('finals_grade', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('overall_grade', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('enrollment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='base.enrollment')),
            ],
        ),
    ]
