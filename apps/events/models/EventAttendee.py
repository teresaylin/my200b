from django.db import models
from django.contrib.auth.models import User

from . import Event

class EventAttendee(models.Model):
    class Meta:
        app_label = 'events'
        unique_together = ('event', 'user')
        
    event = models.ForeignKey(Event)
    user = models.ForeignKey(User)