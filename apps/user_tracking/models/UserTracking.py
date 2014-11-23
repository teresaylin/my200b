from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import utc

class UserTracking(models.Model):
    user = models.OneToOneField(User, related_name='tracking', primary_key=True)
    lastSeen = models.DateTimeField()
    
    def isOnline(self):
        return (datetime.utcnow().replace(tzinfo=utc) - self.lastSeen) < timedelta(seconds=30)