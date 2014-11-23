from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.conf import settings

class AppView(TemplateView):
    template_name = "webapp/app.html"
    
    def get(self, request, *args, **kwargs):
        # Redirect to login page if not authenticated
        if request.user.is_authenticated():
            return super().get(request, *args, **kwargs)
        else:
            return redirect(settings.LOGIN_URL)