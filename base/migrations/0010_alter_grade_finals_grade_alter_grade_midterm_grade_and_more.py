# Generated by Django 5.1.2 on 2024-11-20 03:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0009_grade'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grade',
            name='finals_grade',
            field=models.DecimalField(blank=True, decimal_places=5, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='grade',
            name='midterm_grade',
            field=models.DecimalField(blank=True, decimal_places=5, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='grade',
            name='overall_grade',
            field=models.DecimalField(blank=True, decimal_places=5, max_digits=10, null=True),
        ),
    ]