from datetime import datetime
from django.utils.timezone import utc

from ..models import UserTracking

class UserTrackingMiddleware(object):
    def process_request(self, request):
        # Ignore unauthenticated users
        if not request.user.is_authenticated():
            return None

        # Update user's lastSeen time
        UserTracking.objects.update_or_create(user=request.user, defaults={
            'lastSeen': datetime.utcnow().replace(tzinfo=utc)
        })