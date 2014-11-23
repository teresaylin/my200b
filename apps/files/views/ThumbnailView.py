from django.views.generic import View
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.core.cache import caches
from django.conf import settings

import dropbox

from ..classes import AppDropboxClient
from ..utils import userPathToDropboxPath

class ThumbnailView(View):

    def get(self, request, path=None, size=None, format=None):
        # Only allow logged-in users
        if not request.user.is_authenticated():
            return HttpResponse('Unauthorized', status=401)

        # Get image size
        size = size.lower()
        if not size in ['xs', 's', 'm', 'l', 'xl']:
            return HttpResponseBadRequest('Invalid image size')

        # Get requested image format
        format = format.upper()
        if not format in ['JPEG', 'PNG']:
            return HttpResponseBadRequest('Invalid file type')

        # Transform user path to Dropbox path
        path = userPathToDropboxPath(path, request.user)
        
        # Lookup thumbnail in cache
        cache = caches['default']
        cacheKey = 'file-thumbnail:%s:%s:%s' % (path, size, format)
        data = cache.get(cacheKey)
        
        if not data:
            # Cache miss, get thumbnail from Dropbox
            cl = AppDropboxClient()
            try:
                apiResponse = cl.thumbnail(path, size, format)
            except dropbox.rest.ErrorResponse as e:
                if e.status == 400:
                    # Bad request
                    return HttpResponseBadRequest()
                elif e.status == 404:
                    # Image not available
                    return HttpResponseNotFound()
                elif e.status == 415:
                    # Invalid image
                    return HttpResponseNotFound()
                else:
                    raise

            data = {
                'content': apiResponse.read(),
                'type': apiResponse.getheader('Content-Type')
            }
                
            # Store in cache
            cache.set(cacheKey, data, settings.FILE_THUMBNAIL_CACHE_TIMEOUT)
        
            # Cleanup
            apiResponse.close()
        
        # Create response
        response = HttpResponse(data['content'], content_type=data['type'])
        response['Cache-Control'] = 'public, max-age=%d' % (settings.FILE_THUMBNAIL_CACHE_TIMEOUT,)
        
        return response