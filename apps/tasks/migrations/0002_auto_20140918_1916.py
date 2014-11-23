# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, to='tasks.Task', related_name='subtasks'),
        ),
    ]
