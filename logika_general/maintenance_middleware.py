from django.shortcuts import render
from django.conf import settings


class MaintenanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.MAINTENANCE_MODE:  # Check your maintenance mode flag here
            return render(request, "maintenance.html", status=503)

        response = self.get_response(request)
        return response
