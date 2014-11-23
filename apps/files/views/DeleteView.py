from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError

import dropbox

from ..classes import AppDropboxClient
from ..utils import userPathToDropboxPath, dropboxPathToUserPath
from ..exceptions import DropboxError, FileNotFound

class DeleteView(APIView):

    def post(self, request):
        # Get paths from request data
        paths = request.DATA.get('paths', None)
        if not paths:
            raise ParseError('No paths given')
        
        # Check paths is an array
        try:
            [ str(s) for s in paths ]
        except:
            raise ParseError('Expected an array of paths')
        
        for path in paths:
            # Transform user path to Dropbox path
            path = userPathToDropboxPath(path, request.user)
            
            # Delete file
            cl = AppDropboxClient()
            try:
                cl.file_delete(path)
            except dropbox.rest.ErrorResponse as e:
                if e.status == 400:
                    raise DropboxError()
                elif e.status == 404:
                    raise FileNotFound()
                else:
                    raise

        return Response({})