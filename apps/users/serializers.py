from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework import serializers

from apps.user_tracking.models import UserTracking
from .models import UserProfile, Role, UserRoleMapping, TaskForce, Team, Milestone, Comment, CommentThread

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('picture_filename', 'phone_number', 'car')
        read_only_fields = ('picture_filename',)
        
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'name', 'user_assignable')

class UserRoleMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRoleMapping
        fields = ('role', 'status')
        
    role = RoleSerializer()
    
class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'color', 'team_email')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'profile', 'user_roles', 'teams', 'is_online')
        
    profile = UserProfileSerializer()
    user_roles = UserRoleMappingSerializer()
    teams = TeamSerializer()
    full_name = serializers.SerializerMethodField('getFullName')
    is_online = serializers.SerializerMethodField('getIsOnline')
    
    def getFullName(self, obj):
        return obj.first_name + ' ' + obj.last_name

    def getIsOnline(self, obj):
        try:
            return obj.tracking.isOnline()
        except UserTracking.DoesNotExist:
            return False
    
class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = ('id', 'name', 'end_date')

class ChildTaskForceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskForce
        fields = ('id', 'name', 'milestone', 'team', 'parent_task_force', 'members')
        
    milestone = MilestoneSerializer(read_only=True)
    members = UserSerializer(read_only=True)

class TaskForceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskForce
        fields = ('id', 'name', 'milestone_id', 'milestone', 'team', 'parent_task_force', 'children', 'members')
        
    milestone_id = serializers.WritableField(source='milestone_id', write_only=True)

    milestone = MilestoneSerializer(read_only=True)
    children = ChildTaskForceSerializer(read_only=True)
    members = UserSerializer(read_only=True)
    
class CommentThreadIdField(serializers.WritableField):
    def to_native(self, obj):
        # Return thread's public ID
        return str(obj.publicId)

    def from_native(self, data):
        # Get thread from public ID
        try:
            publicId = int(data)
            thread = CommentThread.objects.get(publicId=publicId)
        except ValueError:
            raise ValidationError('Invalid thread ID')
        except CommentThread.DoesNotExist:
            raise ValidationError('Thread not found')
        
        return thread
    
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('thread', 'time', 'user', 'body')
        read_only_fields = ('time',)
        
    thread = CommentThreadIdField(write_only=True)
    user = UserSerializer(read_only=True)