# myapp/middleware.py

from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:
    """
    Middleware that requires a user to be authenticated to access certain views.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of URL names that don't require authentication
        exempt_urls = [
            reverse("login"),
            # Add other URLs that should be accessible without login
        ]

        # Check if the user is not authenticated and the requested URL is not exempt
        if not request.user.is_authenticated and request.path not in exempt_urls:
            return redirect("login")  # Redirect to the login page

        response = self.get_response(request)
        return response
