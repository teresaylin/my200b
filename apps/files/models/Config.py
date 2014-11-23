from datetime import datetime
from django.db import models
from django.utils.timezone import utc

class Config(models.Model):
    MIN_TIME = datetime.min.replace(tzinfo=utc)
    def getMinTime():
        return Config.MIN_TIME

    deltaCursor = models.CharField(max_length=512, null=True)
    lastDeltaSync = models.DateTimeField(default=getMinTime)
    
    def save(self, *args, **kwargs):
        Config.objects.exclude(id=self.id).delete()
        return super().save(*args, **kwargs)
    
    @staticmethod
    def load():
        try:
            return Config.objects.get()
        except:
            return Config()