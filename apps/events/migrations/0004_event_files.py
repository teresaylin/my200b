# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0005_auto_20141007_1817'),
        ('events', '0003_auto_20140921_1746'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='files',
            field=models.ManyToManyField(blank=True, to='files.FileAppData'),
            preserve_default=True,
        ),
    ]
