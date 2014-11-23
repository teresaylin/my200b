# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import apps.files.models.Config


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0003_auto_20141005_1444'),
    ]

    operations = [
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('deltaCursor', models.CharField(max_length=512, null=True)),
                ('lastDeltaSync', models.DateTimeField(default=apps.files.models.Config.getMinTime)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
