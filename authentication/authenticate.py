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
        # First try to get token from cookies (HTTP-only cookies are more secure)
        raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])
        
        # Only try Authorization header if no cookie token and header doesn't contain "null"
        if raw_token is None:
            header = self.get_header(request)
            if header is not None:
                raw_token = self.get_raw_token(header)
                # Check if the token is "null" or empty
                if raw_token and raw_token.decode('utf-8') in ['null', '']:
                    raw_token = None

        if raw_token is None:
            return None
        
        try:
            validated_token = self.get_validated_token(raw_token)
            # Only enforce CSRF for non-GET requests or when explicitly needed
            if request.method != 'GET':
                enforce_csrf(request)
            return self.get_user(validated_token), validated_token
        except Exception as e:
            # If token validation fails, return None to allow other auth methods
            return None
        
