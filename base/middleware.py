from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # URLs that don't require login
        self.public_urls = [
            reverse('base:login'),
            reverse('base:register'),
            reverse('base:admin_register'),
            reverse('base:home'),
        ]

    def __call__(self, request):
        if not request.user.is_authenticated and request.path not in self.public_urls:
            messages.warning(request, 'Please login to access this page.')
            return redirect('base:login')

        response = self.get_response(request)
        return response 