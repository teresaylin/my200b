# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_event_alive'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='alive',
            field=models.BooleanField(default=True, editable=False),
        ),
    ]
