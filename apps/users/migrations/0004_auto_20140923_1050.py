# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_commentthread_publicid'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='userteammapping',
            unique_together=set([('user', 'team')]),
        ),
    ]
