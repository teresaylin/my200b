from rest_framework import serializers

from ..models import FileAppData

class FileAppDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileAppData
        fields = ('comment_thread',)
    
    comment_thread = serializers.SerializerMethodField('getCommentThread')
    def getCommentThread(self, obj):
        return str(obj.comment_thread.publicId)