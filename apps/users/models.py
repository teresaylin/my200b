from django.db import models
from django.db.models.signals import post_save
from django.db import IntegrityError
from django.contrib.auth.models import User

from libs.softdelete.models import SoftDeleteableModel

from random import SystemRandom
rngSource = SystemRandom()

class Team(models.Model):
    color = models.CharField(max_length=10, blank = False)
    team_email = models.EmailField(max_length=30)
    users = models.ManyToManyField(User, through='UserTeamMapping', related_name='teams')

    def __str__(self):
        return self.color

class UserTeamMapping(models.Model):
    class Meta:
        unique_together = ('user', 'team')

    user = models.ForeignKey(User)
    team = models.ForeignKey('Team')
    section = models.CharField(max_length=15, blank = True)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name + " ("+ self.user.email +") - " + self.team.color + "/ " + self.section
        #return u"%s %s (%s): %s" % (self.user.first_name, self.user.last_name, self.user.email, self.team.color)

class Role(models.Model):
    name = models.CharField(max_length=50)
    required_role = models.ForeignKey('Role', null=True, blank=True, related_name='required_by')
    user_assignable = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class UserRoleMapping(models.Model):
    class Meta:
        unique_together = ('user', 'role')

    user = models.ForeignKey(User, related_name="user_roles")
    role = models.ForeignKey('Role')
    status = models.CharField(max_length=50, blank = True)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name + " " + self.status

class UserProfile(models.Model):
    CAR_CHOICES = (
        ('Y', 'Yes'),
        ('N', 'No'),
    )

    user = models.OneToOneField(User, related_name='profile', primary_key=True)
    picture_filename = models.CharField(max_length=20, blank=True)
    phone_number = models.CharField(max_length=12)
    car = models.CharField(max_length=1, choices=CAR_CHOICES)

    def __str__(self):
        return str(self.user)
    
    @staticmethod
    def onUserSave(sender, **kwargs):
        # Create UserProfile object when a User is created
        user = kwargs['instance']
        if kwargs['created']:
            UserProfile.objects.create(
                user=user,
                picture_filename='',
                phone_number='',
                car='N'
            )
post_save.connect(UserProfile.onUserSave, sender=User)

class Milestone(models.Model):
    name = models.CharField(max_length=50)
    end_date = models.DateField()

    def __str__(self):
        return self.name + " " + str(self.end_date)

class TaskForce(SoftDeleteableModel):
    name = models.CharField(max_length=50, blank = False)
    milestone = models.ForeignKey('Milestone')
    team = models.ForeignKey('Team')
    parent_task_force = models.ForeignKey('TaskForce', blank = True, null = True, related_name='children')
    members = models.ManyToManyField(User, related_name='taskforces')
    #URL

    def __str__(self):
        return self.name + "- " + str(self.milestone)
    
    def delete(self, *args, **kwargs):
        # Delete sub taskforces
        for tf in self.children.all():
            tf.delete()
            
        return super().delete(*args, **kwargs)

class UserTaskForceMapping(models.Model):
    user = models.ForeignKey(User)
    task_force = models.ForeignKey('TaskForce')

    def __str__(self):
        return str(self.user) + "- " + str(self.task_force)

class CommentThread(SoftDeleteableModel):
    publicId = models.BigIntegerField(unique=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.publicId:
            # Assign random public ID
            while True:
                self.publicId = rngSource.randint(1, models.BigIntegerField.MAX_BIGINT)
                try:
                    super().save(*args, **kwargs)
                    break
                except IntegrityError:
                    # Retry in the super-rare event that the ID is already taken
                    continue
        else:
            super().save(*args, **kwargs)
    
class Comment(SoftDeleteableModel):
    thread = models.ForeignKey(CommentThread, related_name='comments')
    time = models.DateTimeField()
    user = models.ForeignKey(User)
    body = models.TextField()