from django.views.generic import View
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from hashlib import sha256
import hmac
import json

from ..tasks import deltaSync

class DropboxWebhookView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        """
        Dropbox checks the webhook end-point by sending a GET request, along with a challenge parameter.
        This challenge parameter should be echoed back to the client.
        """
        challenge = request.GET.get('challenge', None)
        if not challenge:
            return HttpResponseBadRequest()

        return HttpResponse(challenge)
    
    def post(self, request):
        # Verify body signature
        signature = request.META.get('HTTP_X_DROPBOX_SIGNATURE', None)
        if signature != hmac.new(settings.DROPBOX_APP_SECRET.encode('ascii'), request.body, sha256).hexdigest():
            return HttpResponseForbidden('Bad signature')
        
        # Decode JSON request body
        data = json.loads(request.body.decode('UTF-8'))
        
        # Synchronize filesystem
        deltaSync()

        return HttpResponse()