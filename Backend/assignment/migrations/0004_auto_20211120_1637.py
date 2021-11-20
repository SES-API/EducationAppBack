# Generated by Django 3.2.8 on 2021-11-20 13:07

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assignment', '0003_auto_20211120_1308'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assignment',
            name='questions',
        ),
        migrations.RemoveField(
            model_name='question',
            name='students',
        ),
        migrations.AddField(
            model_name='question',
            name='assignment_fk',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='assignment_question', to='assignment.assignment'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='question',
            name='is_graded',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='grade',
            name='delay',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='grade',
            name='value',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
    ]
