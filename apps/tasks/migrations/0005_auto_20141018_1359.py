# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_task_files'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='assigned_taskforces',
            field=models.ManyToManyField(related_name='assigned_tasks', blank=True, to='users.TaskForce'),
        ),
    ]
