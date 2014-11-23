from rest_framework import serializers
from libs.permissions.user_permissions import getUserObjectPermissions

class ObjectPermissionsSerializerMixin(object):
    def get_fields(self):
        fields = super().get_fields()
        fields['_permissions'] = serializers.SerializerMethodField('getObjectPermissions')
        return fields
    
    def getObjectPermissions(self, obj):
        return getUserObjectPermissions(self.context['request'].user, obj)