# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-03-27 14:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('python_management', '0003_added_unique_constraint'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pythonmanagementdeleterequest',
            name='virtual_env_name',
        ),
        migrations.RemoveField(
            model_name='pythonmanagementfindvirtualenvsrequest',
            name='virtual_env_name',
        ),
    ]
