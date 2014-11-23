from rest_framework import serializers

class FileAppDataUserPathField(serializers.RelatedField):
    def to_native(self, value):
        return value.getUserPath()