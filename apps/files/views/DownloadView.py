from django.views.generic import View
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.conf import settings
from django.shortcuts import redirect

import dropbox

from ..classes import AppDropboxClient
from ..utils import userPathToDropboxPath

class DownloadView(View):

    def get(self, request, path=None):
        # Redirect to login page if not authenticated
        if not request.user.is_authenticated():
            return redirect(settings.LOGIN_URL)

        # Transform user path to Dropbox path
        path = userPathToDropboxPath(path, request.user)
        
        # Get share link from Dropbox
        cl = AppDropboxClient()
        try:
            link = cl.share(path, short_url=False)
        except dropbox.rest.ErrorResponse as e:
            if e.status == 400:
                # Bad request
                return HttpResponseBadRequest(str(e))
            elif e.status == 404:
                # File not found
                return HttpResponseNotFound('File not found')
            else:
                raise
        
        return redirect(link['url'])