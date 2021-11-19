# Generated by Django 3.2.8 on 2021-11-19 11:18

import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('class_app', '0002_auto_20211118_1342'),
    ]

    operations = [
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('delay', models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('weight', models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('students', models.ManyToManyField(related_name='question_student', through='assignment.Grade', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='grade',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assignment.question'),
        ),
        migrations.AddField(
            model_name='grade',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('date', models.DateField(default=datetime.date.today)),
                ('class_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignment_class', to='class_app.class')),
                ('questions', models.ManyToManyField(related_name='assignment_question', to='assignment.Question')),
            ],
        ),
    ]
