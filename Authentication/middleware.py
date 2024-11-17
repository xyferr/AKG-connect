import logging
from django.shortcuts import redirect
from .models import TokenModel



class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # logger.debug(f"Request path: {request.path}")
        user_id = request.session.get('user_id')
        # logger.debug(f"User ID in session: {user_id}")

        # Check if the request path is not the login path
        if not request.path.startswith('/auth/login/') and not request.path.startswith('/admin/'):
            # Check if the user ID is stored in the session
            if not user_id:
                print("User ID not found in session, redirecting to login")
                return redirect('login')

            # Check if there is a token associated with the user ID
            if not TokenModel.objects.filter(user_id=user_id).exists():
                # logger.debug("No token associated with user ID, redirecting to login")
                return redirect('login')

        # Proceed with the request if the user is authenticated
        response = self.get_response(request)
        return response