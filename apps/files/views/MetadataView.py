from django.core.cache import caches
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError

import dropbox

from ..classes import AppDropboxClient
from ..utils import userPathToDropboxPath, dropboxPathToUserPath
from ..exceptions import FileNotFound
from ..models import FileAppData
from ..serializers import FileAppDataSerializer

class MetadataView(APIView):
    
    def get(self, request, path=None):
        # Transform user path to Dropbox path
        path = userPathToDropboxPath(path, request.user)
        
        # Create Dropbox client object
        client = AppDropboxClient()
        
        # Lookup metadata in cache
        cache = caches['default']
        cacheKey = 'file-metadata:%s' % (path,)
        cacheData = cache.get(cacheKey)
        
        # Retrieve metadata
        try:
            data = client.metadata(path, hash=cacheData.get('hash', None) if cacheData else None)

            # Cache directory listings
            if data['is_dir']:
                cache.set(cacheKey, data, settings.FILE_METADATA_CACHE_TIMEOUT)
        except dropbox.rest.ErrorResponse as e:
            if e.status == 304:
                # Folder unchanged, use cached data
                data = cacheData
            elif e.status == 404:
                raise FileNotFound()
            else:
                raise
            
        # Inject local app data
        if data['is_dir']:
            if 'contents' in data:
                fileMap = {}
                for file in data['contents']:
                    if file['is_dir']:
                        continue
                    fileMap[file['path'].lower()] = file
                    
                dataObjs = FileAppData.objects.filter(path__in=fileMap.keys())
                for dataObj in dataObjs:
                    fileMap[dataObj.path]['app_data'] = FileAppDataSerializer(dataObj).data
        else:
            try:
                dataObj = FileAppData.objects.get(path=data['path'].lower())
                data['app_data'] = FileAppDataSerializer(dataObj).data
            except FileAppData.DoesNotExist:
                pass

        # Transform Dropbox paths to user paths
        data['path'] = dropboxPathToUserPath(data['path'])
        if 'contents' in data:
            for file in data['contents']:
                file['path'] = dropboxPathToUserPath(file['path'])
            
        return Response(data)