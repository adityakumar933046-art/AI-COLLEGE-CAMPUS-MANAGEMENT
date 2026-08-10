from django.shortcuts import redirect
from django.urls import reverse

class MustChangePasswordMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and getattr(request.user, 'must_change_password', False):
            change_pwd_url = reverse('change_password')
            logout_url = reverse('logout')
            current_path = request.path

            if not (current_path.startswith(change_pwd_url) or current_path.startswith(logout_url) or current_path.startswith('/static/') or current_path.startswith('/media/')):
                return redirect('change_password')

        return self.get_response(request)
