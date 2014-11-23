from rest_framework.decorators import action
from rest_framework.response import Response

from ..exceptions import FileNotFound
from ..models import FileAppData
from ..utils import userPathToDropboxPath

class ModelWithFilesViewSetMixin(object):
    
    @action(methods=['PUT'])
    def add_file(self, request, pk=None):
        obj = self.get_object()
        
        # Get file path
        path = request.DATA.get('path', None)
        if not path:
            raise ParseError('No path specified')
        try:
            path = str(path)
        except ValueError:
            raise ParseError('Invalid path')
        
        # Transform user path to Dropbox path
        path = userPathToDropboxPath(path, request.user)
        
        # Get FileAppData object
        try:
            file = FileAppData.objects.get(path=path.lower())
        except FileAppData.DoesNotExist:
            raise FileNotFound()
        
        # Add file to files list
        obj.files.add(file)
        
        return Response({})

    @action(methods=['PUT'])
    def remove_file(self, request, pk=None):
        obj = self.get_object()

        # Get file path
        path = request.DATA.get('path', None)
        if not path:
            raise ParseError('No path specified')
        try:
            path = str(path)
        except ValueError:
            raise ParseError('Invalid path')

        # Transform user path to Dropbox path
        path = userPathToDropboxPath(path, request.user)
        
        # Get FileAppData object
        try:
            file = obj.files.get(path=path.lower())
        except FileAppData.DoesNotExist:
            raise FileNotFound()
        
        # Remove file from list
        obj.files.remove(file)
        
        return Response({})