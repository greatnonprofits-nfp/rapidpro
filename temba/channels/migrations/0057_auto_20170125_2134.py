# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-25 21:34
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('channels', '0056_remove_channelsession_parent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='channelsession',
            name='flow',
        ),
        migrations.RemoveField(
            model_name='channelsession',
            name='parent',
        ),
    ]
