# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0005_auto_20141007_1817'),
        ('tasks', '0003_task_alive'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='files',
            field=models.ManyToManyField(to='files.FileAppData', blank=True),
            preserve_default=True,
        ),
    ]
