# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-07 01:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csa', '0003_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='member',
            name='code',
        ),
        migrations.AddField(
            model_name='member',
            name='exclusions',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='member',
            name='isActive',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='member',
            name='phone',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='name',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]
