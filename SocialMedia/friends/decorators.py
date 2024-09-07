from functools import wraps
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from .backends import EmailBackend

def validate_token(view_func):
    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return JsonResponse({'error': 'Authorization header missing'}, status=401)
        
        if not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Invalid token type'}, status=401)
        
        token = auth_header.split(' ')[1]
        user = get_user_from_token(token)
        if not user:
            return JsonResponse({'error': 'Invalid token'}, status=401)
        
        request.user = user  # Attach the user to the request object
        
        return view_func(self, request, *args, **kwargs)
    return _wrapped_view

def get_user_from_token(token):
    try:
        access_token = AccessToken(token)
        user_id = access_token['user_id']
        backend = EmailBackend()
        user = backend.get_user(user_id)
        return user
    except TokenError:
        return None
