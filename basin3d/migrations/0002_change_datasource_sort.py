# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-09-20 16:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('basin3d', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='datasource',
            options={'ordering': ['id_prefix']},
        ),
    ]
