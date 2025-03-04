from django.shortcuts import render
from .models import SiteSettings

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if SiteSettings.objects.first().maintenance_mode:
            return render(request, 'website/maintenance.html', status=503)
        return self.get_response(request)