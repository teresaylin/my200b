# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20140923_1050'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='required_role',
            field=models.ForeignKey(null=True, to='users.Role', related_name='required_by', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='role',
            name='user_assignable',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
