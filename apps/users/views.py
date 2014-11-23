from datetime import datetime

from django.utils.timezone import utc
from django.db.models import Q
from django.db import IntegrityError
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ParseError

from libs.permissions.user_permissions import getUserObjectPermissions

from .models import TaskForce, Team, UserProfile, Milestone, Comment, CommentThread, Role, UserRoleMapping
from .serializers import TaskForceSerializer, TeamSerializer, UserSerializer, UserProfileSerializer, MilestoneSerializer, CommentSerializer, RoleSerializer, UserRoleMappingSerializer
from .exceptions import UserNotFound, UserAlreadyHasRole, CommentThreadNotFound

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Return only teams logged-in user belongs to if 'current' parameter is given
        current = self.request.QUERY_PARAMS.get('current', None)
        if current is not None:
            queryset = queryset.filter(users__in=[self.request.user])
        
        return queryset

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_fields = ('teams',)
    ordering = ('last_name',)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Return only logged-in user if 'current' parameter is given
        current = self.request.QUERY_PARAMS.get('current', None)
        if current is not None:
            queryset = queryset.filter(pk=self.request.user.id)
            
        # Perform name search
        searchName = self.request.QUERY_PARAMS.get('search_name', None)
        if searchName is not None:
            if ' ' in searchName:
                # Search by partial full name (e.g. John Smi)
                tok = searchName.split(' ', 1)
                queryset = queryset.filter(first_name__iexact=tok[0], last_name__istartswith=tok[1])
            else:
                # Search first name or last name
                queryset = queryset.filter(Q(first_name__icontains=searchName) | Q(last_name__icontains=searchName))
            
        return queryset

    @action(methods=['PUT'])
    def add_role(self, request, pk=None):
        user = self.get_object()
        
        # Get Role object
        try:
            roleId = request.DATA.get('role_id', None)
            role = Role.objects.get(id=roleId)
        except Role.DoesNotExist:
            raise RoleNotFound()
        
        # Check role is user assignable
        if not role.user_assignable:
            raise PermissionDenied()
        
        # Check user has required parent role
        if role.required_role:
            if not role.required_role in [userRole.role for userRole in user.user_roles.all()]:
                raise PermissionDenied()
        
        # Create UserRoleMapping object
        try:
            userRole = UserRoleMapping.objects.create(
                user=user,
                role=role,
                status=''
            )
        except IntegrityError:
            raise UserAlreadyHasRole()
            
        return Response(UserRoleMappingSerializer(userRole).data)

    @action(methods=['PUT'])
    def remove_role(self, request, pk=None):
        user = self.get_object()
        
        # Find UserRole object
        try:
            roleId = request.DATA.get('role_id', None)
            userRole = user.user_roles.all().get(role__id=roleId)
        except UserRoleMapping.DoesNotExist:
            raise RoleNotFound()

        # Check role is user assignable
        if not userRole.role.user_assignable:
            raise PermissionDenied()
        
        # Delete UserRole object
        userRole.delete()
        
        return Response({})

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    filter_fields = ('user',)
    
class TaskForceViewSet(viewsets.ModelViewSet):
    queryset = TaskForce.objects.all()
    serializer_class = TaskForceSerializer
    filter_fields = ('team', 'parent_task_force')
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Show only task forces where parent_task_force = null, if "root" param is given
        root = self.request.QUERY_PARAMS.get('root', None)
        if root is not None:
            queryset = queryset.filter(parent_task_force=None)

        # Perform name search
        searchName = self.request.QUERY_PARAMS.get('search_name', None)
        if searchName is not None:
            queryset = queryset.filter(name__icontains=searchName)
            
        return queryset
    
    def pre_save(self, obj):
        # Ensure sub-tasks inherit their parent's milestone
        if obj.parent_task_force:
            obj.milestone = obj.parent_task_force.milestone

        if obj.parent_task_force:
            # Only allow sub-taskforce creation if user has update permission on parent
            perm = getUserObjectPermissions(self.request.user, obj.parent_task_force)
            if not perm['update']:
                raise PermissionDenied()
            
            # Ensure sub-taskforces have same team as parent
            obj.team = obj.parent_task_force.team

        # Ensure user can only create taskforces for teams they belong to
        if not obj.team in self.request.user.teams.all():
            raise PermissionDenied()
            
    def update(self, request, pk=None):
        # Ensure milestone cannot be changed after the task force has been created
        taskforce = self.get_object()
        request.DATA['milestone_id'] = taskforce.milestone.id;
        
        return super().update(request, pk=pk)

    @action(methods=['PUT'])
    def add_member(self, request, pk=None):
        taskforce = self.get_object()
        
        # Get User object from task force's team members; prevents non team members from being added
        try:
            userId = request.DATA.get('user_id', None)
            user = taskforce.team.users.all().get(id=userId)
        except User.DoesNotExist:
            raise UserNotFound()
        
        # Add user to members
        taskforce.members.add(user)
        
        return Response({})

    @action(methods=['PUT'])
    def remove_member(self, request, pk=None):
        taskforce = self.get_object()
        
        # Get User object
        try:
            userId = request.DATA.get('user_id', None)
            user = taskforce.members.all().get(id=userId)
        except User.DoesNotExist:
            raise UserNotFound()
        
        # Remove user from members
        taskforce.members.remove(user)
        
        return Response({})
    
class MilestoneViewSet(viewsets.ModelViewSet):
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer
    ordering = ('end_date',)
    
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    lookup_field = 'publicId'
    serializer_class = CommentSerializer
    ordering = ('-time',)
    
    def get_queryset(self):
        if 'thread' in self.request.QUERY_PARAMS:
            # Lookup comments by public thread ID
            try:
                id = int(self.request.QUERY_PARAMS.get('thread'))
            except ValueError:
                raise ParseError('Invalid thread ID')

            try:
                thread = CommentThread.objects.get(publicId=id)
            except CommentThread.DoesNotExist:
                raise CommentThreadNotFound()
                
            return Comment.objects.all().filter(thread=thread)
        else:
            # Disallow comment listing unless 'thread' parameter is passed
            return Comment.objects.none()

    def pre_save(self, obj):
        # Set user
        obj.user = self.request.user

        # Set time to now
        obj.time = datetime.utcnow().replace(tzinfo=utc)
        
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()

        if 'user_assignable' in self.request.QUERY_PARAMS:
            # Return only roles that the current user can assign themselves
            roles = [userRole.role for userRole in self.request.user.user_roles.all()]
            queryset = queryset.filter(
                user_assignable=True,
                required_role__in=roles
            )

        return queryset