# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20140923_1050'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileAppData',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('dropbox_path', models.CharField(unique=True, max_length=512)),
                ('comment_thread', models.OneToOneField(to='users.CommentThread')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
