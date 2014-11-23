# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0002_auto_20141002_1455'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileappdata',
            name='comment_thread',
            field=models.OneToOneField(to='users.CommentThread'),
        ),
    ]
