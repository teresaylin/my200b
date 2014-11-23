from django.views.generic import View
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.conf import settings
from django.shortcuts import redirect

import dropbox

from ..classes import AppDropboxClient
from ..utils import userPathToDropboxPath

class PreviewView(View):

    def get(self, request, path=None):
        # Redirect to login page if not authenticated
        if not request.user.is_authenticated():
            return redirect(settings.LOGIN_URL)

        # Transform user path to Dropbox path
        path = userPathToDropboxPath(path, request.user)
        
        # Get file preview from Dropbox
        cl = AppDropboxClient()
        try:
            apiResponse = cl.preview(path)
        except dropbox.rest.ErrorResponse as e:
            if e.status == 400:
                # Bad request
                return HttpResponseBadRequest(str(e))
            elif e.status == 404:
                # File not found
                return HttpResponseNotFound('File not found')
            elif e.status == 409:
                # Preview unavailable
                return HttpResponseNotFound('Preview unavailable')
            else:
                raise
        
        # Create response
        data = apiResponse.read()
        response = HttpResponse(data, content_type=apiResponse.getheader('Content-Type'))
        
        # Cleanup
        apiResponse.close()
        
        return response