from django.contrib.auth.models import User
from apps.events.models import Event
from apps.tasks.models import Task
from apps.users.models import Comment, Milestone, Role, TaskForce, Team, UserProfile

def filterQueryset(queryset, user):
    """This function performs permission checks and filters querysets appropriately, before they are serialized and sent out as API responses."""
    
    # Bypass filtering for superusers
    if user.is_superuser:
        return queryset

    cls = queryset.model
    
    if cls == Comment:
        # All comments visible to all users
        return queryset
    elif cls == Event:
        # Only show events belonging to user's teams
        return queryset.filter(owner__teams__in=user.teams.all())
    elif cls == Milestone:
        # All milestones visible to all users
        return queryset
    elif cls == Role:
        # Roles visible to all users
        return queryset
    elif cls == Task:
        # Only show tasks belonging to user's teams
        return queryset.filter(owner__teams__in=user.teams.all())
    elif cls == TaskForce:
        # Only show task forces belonging to user's teams
        return queryset.filter(team=user.teams.all())
    elif cls == Team:
        # Teams visible to all users
        return queryset
    elif cls == User:
        # Users visible to all users
        return queryset
    elif cls == UserProfile:
        # User profiles visible to all users
        return queryset
    else:
        raise PermissionDenied()

def getUserPermissions(user, cls):
    """This returns user permissions on a per-model basis."""
    
    # Superuser has full permissions
    if user.is_superuser:
        return {
            'create': True,
            'read': True,
            'update': True,
            'delete': True,
        }

    perms = {
        'create': False,
        'read': False,
        'update': False,
        'delete': False
    }
    
    if cls == Comment:
        # Users can create/read comments
        perms['create'] = True
        perms['read'] = True
    elif cls == Event:
        # Users can create/read/update/delete events
        perms['create'] = True
        perms['read'] = True
        perms['update'] = True
        perms['delete'] = True
    elif cls == Milestone:
        # Users can see milestones
        perms['read'] = True
    elif cls == Role:
        # Users can see roles
        perms['read'] = True
    elif cls == Task:
        # Users can create/read/update/delete tasks
        perms['create'] = True
        perms['read'] = True
        perms['update'] = True
        perms['delete'] = True
    elif cls == TaskForce:
        # Users can create/read/update/delete task forces
        perms['create'] = True
        perms['read'] = True
        perms['update'] = True
        perms['delete'] = True
    elif cls == Team:
        # Users can see teams
        perms['read'] = True
    elif cls == User:
        # Users can see/update users
        perms['read'] = True
        perms['update'] = True
    elif cls == UserProfile:
        # Users can see and update profiles
        perms['read'] = True
        perms['update'] = True
        
    return perms

def getUserObjectPermissions(user, obj):
    """This returns user permissions on a per-object basis."""

    # Superuser has full permissions
    if user.is_superuser:
        return {
            'read': True,
            'update': True,
            'delete': True,
        }

    # Note: it is implied the user can read the object as this function should be called after the
    # queryset containing the object has been filtered through filterQueryset()
    perms = {
        'read': True,
        'update': False,
        'delete': False
    }

    cls = obj.__class__
    
    if cls == Event:
        # User can update/delete events they own
        if obj.owner == user:
            perms['update'] = True
            perms['delete'] = True
    elif cls == Task:
        # User can update/delete tasks they own
        if obj.owner == user:
            perms['update'] = True
            perms['delete'] = True
            
        # Users assigned to task can edit task
        if user in obj.assigned_users.all():
            perms['update'] = True
            
        # Users, belonging to a task force which is assigned to this task, can edit task
        if user in User.objects.filter(taskforces__assigned_tasks__in=[obj]):
            perms['update'] = True
    elif cls == TaskForce:
        # User can edit task forces belonging to teams to which they are assigned
        if obj.team in user.teams.all():
            perms['update'] = True
            perms['delete'] = True
    elif cls == User:
        # User can update own User object
        if obj == user:
            perms['update'] = True
    elif cls == UserProfile:
        # User can update own profile
        if obj.user == user:
            perms['update'] = True
        
    return perms