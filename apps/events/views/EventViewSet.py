from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Q
from django.contrib.auth.models import User

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from apps.users.exceptions import UserNotFound, TeamNotFound, TaskForceNotFound
from apps.users.models import Team, TaskForce

from apps.files.views import ModelWithFilesViewSetMixin

from ..exceptions import EventAlreadyHasAttendee, EventEndPrecedesStart
from ..models import Event, EventAttendee
from ..serializers import EventSerializer

class EventViewSet(ModelWithFilesViewSetMixin, viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    #filter_fields = ('teams',)
    ordering = ('start',)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Get time filter parameters
        start = self.request.QUERY_PARAMS.get('start', None)
        end = self.request.QUERY_PARAMS.get('end', None)

        try:
            # Filter by time range
            if start is not None:
                queryset = queryset.filter(Q(start__gt=start) | Q(end__gt=start))
            if end is not None:
                queryset = queryset.filter(start__lt=end)
        except ValidationError:
            raise ParseError('Invalid date')
        
        # Filter by team
        teamId = self.request.QUERY_PARAMS.get('team', None)
        if teamId:
            try:
                team = Team.objects.get(id=teamId)
            except ValueError:
                raise ParseError('Invalid team ID')
            except Team.DoesNotExist:
                raise TeamNotFound()
            queryset = queryset.filter(owner__teams__in=[team])
        
        return queryset
    
    def pre_save(self, obj):
        # Set owner when object is created
        if not obj.pk:
            obj.owner = self.request.user
        
        # Check start time precedes end time
        if obj.end < obj.start:
            raise EventEndPrecedesStart()
        
    @action(methods=['PUT'])
    def add_attendee(self, request, pk=None):
        event = self.get_object()
        
        # Get attendee User object
        try:
            userId = request.DATA.get('user_id', None)
            user = User.objects.get(id=userId)
        except User.DoesNotExist:
            raise UserNotFound()
        
        # Create EventAttendee object
        try:
            EventAttendee.objects.create(
                event=event,
                user=user
            )
        except IntegrityError:
            raise EventAlreadyHasAttendee()
        
        return Response({})

    @action(methods=['PUT'])
    def add_attendee_taskforce(self, request, pk=None):
        event = self.get_object()
        
        # Get TaskForce object
        try:
            taskforceId = request.DATA.get('taskforce_id', None)
            taskforce = TaskForce.objects.get(id=taskforceId)
        except TaskForce.DoesNotExist:
            raise TaskForceNotFound()
        
        # Create EventAttendee objects for taskforce's users
        for user in taskforce.members.all():
            try:
                EventAttendee.objects.create(
                    event=event,
                    user=user
                )
            except IntegrityError:
                # Ignore members of the taskforce that are already attendees
                pass
            
        # Return updated event
        return Response(EventSerializer(event, context={'request': request}).data)

    @action(methods=['PUT'])
    def remove_attendee(self, request, pk=None):
        event = self.get_object()
        
        # Get attendee User object
        try:
            userId = request.DATA.get('user_id', None)
            eventAttendee = EventAttendee.objects.get(event=event, user__id=userId)
        except EventAttendee.DoesNotExist:
            raise UserNotFound()
        
        # Remove EventAttendee object
        eventAttendee.delete()
        
        return Response({})