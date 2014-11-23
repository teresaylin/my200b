# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserTracking',
            fields=[
                ('user', models.OneToOneField(related_name='tracking', to=settings.AUTH_USER_MODEL, primary_key=True, serialize=False)),
                ('lastSeen', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
