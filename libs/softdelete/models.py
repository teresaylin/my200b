from django.db import models

class SoftDeleteableQuerySet(models.QuerySet):
    def delete(self):
        return super().update(alive=False)

    def undelete(self):
        return super().update(alive=True)
    
    def hardDelete(self):
        return super().delete()

    def alive(self):
        return self.filter(alive=True)
    
    def dead(self):
        return self.exclude(alive=True)

class SoftDeleteableManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteableQuerySet(self.model).alive()
    
    def allDead(self):
        return SoftDeleteableQuerySet(self.model).dead()

class SoftDeleteableModel(models.Model):
    class Meta:
        abstract = True

    alive = models.BooleanField(default=True, editable=False)
    
    objects = SoftDeleteableManager()
    
    def delete(self):
        self.alive = False
        self.save()
        
    def undelete(self):
        self.alive = True
        self.save()
        
    def hardDelete(self):
        super().delete()