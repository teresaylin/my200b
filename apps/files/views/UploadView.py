from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError

import dropbox

from ..classes import AppDropboxClient
from ..utils import userPathToDropboxPath, dropboxPathToUserPath

class UploadView(APIView):

    def post(self, request):
        # Check file was sent in request
        if not 'file' in request.FILES:
            return HttpResponseBadRequest('No file given')
        file = request.FILES['file']
        
        # Get path
        path = request.POST.get('path', None)
        if not path:
            raise ParseError('No path given')
        
        # Get parent file revision
        parentRev = request.POST.get('parent_rev', None)
        
        # Transform user path to Dropbox path
        path = userPathToDropboxPath(path, request.user)

        # Upload file to Dropbox
        cl = AppDropboxClient()
        try:
            data = cl.put_file(path, file, overwrite=False, parent_rev=parentRev)
        except dropbox.rest.ErrorResponse as e:
            if e.status == 400:
                raise DropboxError(str(e))
            else:
                raise
            
        # Transform Dropbox path to user path
        data['path'] = dropboxPathToUserPath(data['path'])
        
        return Response(data, status=201)