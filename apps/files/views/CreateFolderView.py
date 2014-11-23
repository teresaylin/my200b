from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError

import dropbox

from ..classes import AppDropboxClient
from ..utils import userPathToDropboxPath, dropboxPathToUserPath
from ..exceptions import DropboxError, FileAlreadyExists

class CreateFolderView(APIView):

    def post(self, request):
        # Get path from request data
        path = request.DATA.get('path', None)
        if not path:
            raise ParseError('No path given')

        # Transform user path to Dropbox path
        path = userPathToDropboxPath(path, request.user)
        
        # Create folder
        cl = AppDropboxClient()
        try:
            data = cl.file_create_folder(path)
        except dropbox.rest.ErrorResponse as e:
            if e.status == 400:
                raise DropboxError()
            elif e.status == 403:
                raise FileAlreadyExists()
            else:
                raise

        # Transform Dropbox path to user path
        data['path'] = dropboxPathToUserPath(data['path'])
        
        return Response(data, status=201)