# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0004_config'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileappdata',
            name='path',
            field=models.CharField(unique=True, db_index=True, max_length=512),
        ),
    ]
