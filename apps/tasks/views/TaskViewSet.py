from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from libs.permissions.user_permissions import getUserObjectPermissions

from apps.users.exceptions import UserNotFound, TaskForceNotFound
from apps.users.models import TaskForce

from apps.files.views import ModelWithFilesViewSetMixin

from ..exceptions import TaskAlreadyAssignedToUser, TaskAlreadyAssignedToTaskForce
from ..models import Task
from ..serializers import TaskSerializer

class TaskViewSet(ModelWithFilesViewSetMixin, viewsets.ModelViewSet):
    queryset = Task.objects.all().exclude(state='completed')
    serializer_class = TaskSerializer
    filter_fields = ('parent',)
    ordering = ('due_time',)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by user
        userId = self.request.QUERY_PARAMS.get('user', None)
        if userId:
            # Get User object
            try:
                user = User.objects.get(id=userId)
            except User.DoesNotExist:
                raise UserNotFound()
            
            queryset = queryset.filter(assigned_users__in=[user])

        # Filter by taskforce
        taskforceId = self.request.QUERY_PARAMS.get('taskforce', None)
        if taskforceId:
            # Get TaskForce object
            try:
                taskforce = TaskForce.objects.get(id=taskforceId)
            except TaskForce.DoesNotExist:
                raise TaskForceNotFound()
            
            queryset = queryset.filter(assigned_taskforces__in=[taskforce])
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        if 'tree' in request.QUERY_PARAMS:
            return self.listTree(request)
        else:
            return super().list(request, *args, **kwargs)
        
    def listTree(self, request):
        """Return results as a tree, starting from any parent tasks that own tasks in the queryset"""
        
        tasks = {}
        rootTasks = []
        
        queryset = self.get_queryset()

        for task in queryset:
            taskData = TaskSerializer(task, context={'request': request}).data
            tasks[task.id] = taskData
            
        def processTask(task):
            if task.parent:
                if task.parent.id in tasks:
                    if not 'subtasks' in tasks[task.parent.id]:
                        tasks[task.parent.id]['subtasks'] = []
                        tasks[task.parent.id]['_hasPartialSubtasks'] = True
                    tasks[task.parent.id]['subtasks'].append(tasks[task.id])
                else:
                    parentData = TaskSerializer(task.parent, context={'request': request}).data
                    parentData['subtasks'] = [ tasks[task.id] ]
                    parentData['_hasPartialSubtasks'] = True
                    tasks[task.parent.id] = parentData
                    processTask(task.parent)
            else:
                rootTasks.append(tasks[task.id])

        for task in queryset:
            processTask(task)
        
        return Response(rootTasks)
    
    def pre_save(self, obj):
        # Set owner when object is created
        if not obj.pk:
            obj.owner = self.request.user
            
        # Only allow subtask creation if user has update permission on parent
        if obj.parent:
            perm = getUserObjectPermissions(self.request.user, obj.parent)
            if not perm['update']:
                raise PermissionDenied()
        
    def post_save(self, obj, created=False):
        # Assign task to owner when object is created
        if created:
            obj.assigned_users.add(obj.owner)
            
    @action(methods=['PUT'])
    def complete(self, request, pk=None):
        task = self.get_object()

        def completeTask(task):
            # Mark subtasks as completed
            for subtask in task.subtasks.all():
                completeTask(subtask)

            # Mark task as completed
            if task.state != task.COMPLETED:
                task.state = task.COMPLETED
                task.completed_by = self.request.user
                task.save()
                
        # Complete task and all subtasks
        completeTask(task)
        
        # Return updated task
        return Response(TaskSerializer(task, context={'request': request}).data)

    @action(methods=['PUT'])
    def add_assigned_user(self, request, pk=None):
        task = self.get_object()
        
        # Get assigned User object
        try:
            userId = request.DATA.get('user_id', None)
            user = User.objects.get(id=userId)
        except User.DoesNotExist:
            raise UserNotFound()
        
        # Assign user to task
        if user in task.assigned_users.all():
            raise TaskAlreadyAssignedToUser()
        else:
            task.assigned_users.add(user)
        
        return Response({})

    @action(methods=['PUT'])
    def remove_assigned_user(self, request, pk=None):
        task = self.get_object()
        
        # Get assigned User object
        try:
            userId = request.DATA.get('user_id', None)
            user = task.assigned_users.all().get(id=userId)
        except User.DoesNotExist:
            raise UserNotFound()
        
        # Remove user assignation
        task.assigned_users.remove(user)
        
        return Response({})

    @action(methods=['PUT'])
    def add_assigned_taskforce(self, request, pk=None):
        task = self.get_object()
        
        # Get TaskForce object
        try:
            taskforceId = request.DATA.get('taskforce_id', None)
            taskforce = TaskForce.objects.get(id=taskforceId)
        except TaskForce.DoesNotExist:
            raise TaskForceNotFound()
        
        # Assign task force to task
        if taskforce in task.assigned_taskforces.all():
            raise TaskAlreadyAssignedToTaskForce()
        else:
            task.assigned_taskforces.add(taskforce)
        
        return Response({})

    @action(methods=['PUT'])
    def remove_assigned_taskforce(self, request, pk=None):
        task = self.get_object()
        
        # Get TaskForce object
        try:
            taskforceId = request.DATA.get('taskforce_id', None)
            taskforce = TaskForce.objects.get(id=taskforceId)
        except TaskForce.DoesNotExist:
            raise TaskForceNotFound()
        
        # Remove task force assignation
        task.assigned_taskforces.remove(taskforce)
        
        return Response({})