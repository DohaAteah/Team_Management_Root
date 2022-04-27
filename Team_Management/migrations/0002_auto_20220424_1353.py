# Generated by Django 3.2.12 on 2022-04-24 10:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Team_Management', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='deadLine',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='task',
            name='dyas_Left',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='task',
            name='is_Done',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='task',
            name='created_Date',
            field=models.DateTimeField(default=datetime.datetime(2022, 4, 24, 13, 53, 23, 503888)),
        ),
    ]