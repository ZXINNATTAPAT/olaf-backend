from rest_framework_simplejwt import authentication as jwt_authentication
from django.conf import settings
from rest_framework import authentication, exceptions as rest_exceptions


def enforce_csrf(request):
    check = authentication.CSRFCheck(request)
    reason = check.process_view(request, None, (), {})
    if reason:
      raise rest_exceptions.PermissionDenied('CSRF Failed: %s' % reason)


class CustomAuthentication(jwt_authentication.JWTAuthentication):
    def authenticate(self, request):
        # First try to get token from Authorization header
        header = self.get_header(request)
        raw_token = None
        
        if header is not None:
            raw_token = self.get_raw_token(header)
        
        # If no token in header, try to get from cookies
        if raw_token is None:
            raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])

        if raw_token is None:
            return None
        
        validated_token = self.get_validated_token(raw_token)
        enforce_csrf(request)
        return self.get_user(validated_token), validated_token
        
