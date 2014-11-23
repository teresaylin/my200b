# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20140921_1746'),
    ]

    operations = [
        migrations.AddField(
            model_name='commentthread',
            name='publicId',
            field=models.BigIntegerField(unique=True, null=True),
            preserve_default=True,
        ),
    ]
