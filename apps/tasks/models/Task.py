from django.db import models
from django.contrib.auth.models import User

from libs.softdelete.models import SoftDeleteableModel
from apps.users.models import CommentThread, TaskForce
from apps.files.models import FileAppData

class Task(SoftDeleteableModel):
    class Meta:
        app_label = 'tasks'
        
    ACTIVE = 'active'
    COMPLETED = 'completed'
    STATES = (
        (ACTIVE, 'Active'),
        (COMPLETED, 'Completed'),
    )

    name = models.CharField(max_length=50, blank=False)
    parent = models.ForeignKey('Task', blank=True, null=True, related_name='subtasks')
    owner = models.ForeignKey(User, related_name='owned_tasks')
    description = models.TextField(blank=True)
    due_time = models.DateTimeField(null=True, blank=True)
    state = models.CharField(max_length=50, choices=STATES, blank=True)
    completed_by = models.ForeignKey(User, related_name='completed_tasks', null=True, blank=True)
    comment_thread = models.OneToOneField(CommentThread)

    assigned_taskforces = models.ManyToManyField(TaskForce, blank=True, related_name='assigned_tasks')
    assigned_users = models.ManyToManyField(User, blank=True)
    
    files = models.ManyToManyField(FileAppData, blank=True)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        # Create comment thread if it doesn't exist
        if not self.comment_thread_id:
            thread = CommentThread.objects.create()
            self.comment_thread = thread
            
        return super().save(*args, **kwargs)
        
    def delete(self, *args, **kwargs):
        # Delete comment thread
        self.comment_thread.delete()
        
        # Delete sub-tasks
        for subtask in self.subtasks.all():
            subtask.delete()
        
        return super().delete(*args, **kwargs)