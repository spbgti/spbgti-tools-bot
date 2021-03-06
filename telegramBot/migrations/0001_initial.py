# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-13 16:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('telegram_id', models.CharField(max_length=12, primary_key=True, serialize=False, unique=True, verbose_name='Id аккаунта телеграм')),
                ('state', models.CharField(default='', max_length=150, verbose_name='Состояние')),
                ('is_student', models.BooleanField(default=False, verbose_name='Учащийся')),
                ('group_number', models.CharField(blank=True, max_length=11, null=True, verbose_name='Номер группы')),
                ('notification_time', models.CharField(blank=True, max_length=10, null=True, verbose_name='Время уведомления')),
            ],
        ),
    ]
