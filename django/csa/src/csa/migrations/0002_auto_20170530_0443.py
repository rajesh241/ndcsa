# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-30 04:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csa', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='areaCode',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
    ]
