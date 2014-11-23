from django.core.cache import caches
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError

import dropbox

from ..classes import AppDropboxClient
from ..utils import userPathToDropboxPath, dropboxPathToUserPath
from ..exceptions import DropboxError
from ..models import FileAppData
from ..serializers import FileAppDataSerializer

class SearchView(APIView):
    
    def get(self, request, path=None):
        # Get query from GET parameters
        query = request.QUERY_PARAMS.get('query', None)
        if not query:
            raise ParseError('No search query specified')

        # Transform user path to Dropbox path
        path = userPathToDropboxPath(path, request.user)
        
        # Create Dropbox client object
        client = AppDropboxClient()
        
        # Search Dropbox
        try:
            data = client.search(path, query, file_limit=10)
        except dropbox.rest.ErrorResponse as e:
            if e.status == 400:
                raise DropboxError()
            else:
                raise

        # Inject local app data
        fileMap = {}
        for file in data:
            if file['is_dir']:
                continue
            fileMap[file['path'].lower()] = file
            
        dataObjs = FileAppData.objects.filter(path__in=fileMap.keys())
        for dataObj in dataObjs:
            fileMap[dataObj.path]['app_data'] = FileAppDataSerializer(dataObj).data

        # Transform Dropbox paths to user paths
        for file in data:
            file['path'] = dropboxPathToUserPath(file['path'])
            
        return Response(data)