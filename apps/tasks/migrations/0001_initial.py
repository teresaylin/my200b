# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('users', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True)),
                ('due_time', models.DateTimeField(null=True, blank=True)),
                ('state', models.CharField(max_length=50, blank=True, choices=[('active', 'Active'), ('completed', 'Completed')])),
                ('assigned_taskforces', models.ManyToManyField(to='users.TaskForce', blank=True)),
                ('assigned_users', models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True)),
                ('comment_thread', models.OneToOneField(to='users.CommentThread')),
                ('completed_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, related_name='completed_tasks', blank=True)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='owned_tasks')),
                ('parent', models.ForeignKey(to='tasks.Task', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
