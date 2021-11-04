# Generated by Django 3.2 on 2021-11-04 15:02

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('class', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='image',
            field=models.ImageField(null=True, upload_to='images/class_pics'),
        ),
        migrations.AlterField(
            model_name='class',
            name='teachers',
            field=models.ManyToManyField(related_name='class_teacher', to=settings.AUTH_USER_MODEL),
        ),
    ]
