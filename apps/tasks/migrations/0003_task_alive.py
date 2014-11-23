# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_auto_20140918_1916'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='alive',
            field=models.BooleanField(default=True, editable=False),
            preserve_default=True,
        ),
    ]
