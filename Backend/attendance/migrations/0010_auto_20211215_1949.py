# Generated by Django 3.2.8 on 2021-12-15 16:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0009_alter_session_end_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='date',
            field=models.DateField(default=datetime.datetime(2021, 12, 15, 19, 49, 25, 840042), null=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='end_time',
            field=models.TimeField(default=datetime.datetime(2021, 12, 15, 21, 49, 25, 840042)),
        ),
    ]
