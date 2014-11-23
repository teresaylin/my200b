# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fileappdata',
            old_name='dropbox_path',
            new_name='path',
        ),
        migrations.AlterField(
            model_name='fileappdata',
            name='comment_thread',
            field=models.OneToOneField(to='users.CommentThread', editable=False),
        ),
    ]
