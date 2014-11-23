from rest_framework import serializers
from libs.permissions.serializers import ObjectPermissionsSerializerMixin

from apps.users.serializers import UserSerializer
from apps.files.serializers import FileAppDataUserPathField

from ..models import Event

class EventSerializer(ObjectPermissionsSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'title', 'owner', 'start', 'end', 'location', 'description', 'comment_thread', 'attendees', 'files')
    
    owner = UserSerializer(read_only=True)
    attendees = UserSerializer(read_only=True)

    files = FileAppDataUserPathField(many=True, read_only=True)

    comment_thread = serializers.SerializerMethodField('getCommentThread')
    def getCommentThread(self, obj):
        return str(obj.comment_thread.publicId)