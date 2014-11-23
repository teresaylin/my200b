# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='alive',
            field=models.BooleanField(default=True, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='commentthread',
            name='alive',
            field=models.BooleanField(default=True, editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='taskforce',
            name='alive',
            field=models.BooleanField(default=True, editable=False),
            preserve_default=True,
        ),
    ]
