# Generated by Django 3.2.8 on 2021-12-03 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('class_app', '0007_alter_university_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='has_password',
            field=models.BooleanField(default=False),
        ),
    ]
