from rest_framework.permissions import BasePermission
from rest_framework.filters import BaseFilterBackend
from rest_framework.exceptions import PermissionDenied

from .user_permissions import getUserPermissions, getUserObjectPermissions, filterQueryset

class ObjectPermissions(BasePermission):
    def has_permission(self, request, view):
        # Allow API root browsing
        if view.__class__.__name__ == 'APIRoot':
            return True
        
        modelCls = getattr(view, 'model', None)
        queryset = getattr(view, 'queryset', None)

        if modelCls is None and queryset is not None:
            modelCls = queryset.model
            
        # Allow access to all non model-related views
        if modelCls is None:
            return True
            
        user = request.user
        perms = getUserPermissions(user, modelCls)
        
        if request.method == 'GET' and perms['read']:
            return True
        elif request.method == 'POST' and perms['create']:
            return True
        elif request.method == 'PUT' and perms['update']:
            return True
        elif request.method == 'DELETE' and perms['delete']:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        modelCls = getattr(view, 'model', None)
        queryset = getattr(view, 'queryset', None)

        if modelCls is None and queryset is not None:
            modelCls = queryset.model

        user = request.user
        perms = getUserObjectPermissions(user, obj)
        
        if request.method == 'GET' and perms['read']:
            return True
        elif request.method == 'PUT' and perms['update']:
            return True
        elif request.method == 'DELETE' and perms['delete']:
            return True
        else:
            return False
        
class ObjectPermissionsFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        user = request.user
        return filterQueryset(queryset, user)