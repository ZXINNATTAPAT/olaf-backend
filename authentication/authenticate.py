from rest_framework_simplejwt import authentication as jwt_authentication
from django.conf import settings
from rest_framework import authentication, exceptions as rest_exceptions


def enforce_csrf(request):
    check = authentication.CSRFCheck(request)
    reason = check.process_view(request, None, (), {})
    if reason:
      raise rest_exceptions.PermissionDenied('CSRF Failed: %s' % reason)


from django.core.cache import cache

class CustomAuthentication(jwt_authentication.JWTAuthentication):
    def authenticate(self, request):
        import logging
        logger = logging.getLogger(__name__)
        
        # First try to get token from cookies (HTTP-only cookies are more secure)
        raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])
        
        # Log cookies for debugging - use INFO level for visibility
        all_cookies = dict(request.COOKIES)
        logger.info(f"🔍 Authentication attempt - Cookies received: {list(all_cookies.keys())}")
        logger.info(f"🔍 All cookies: {all_cookies}")
        logger.info(f"🔍 Looking for cookie: {settings.SIMPLE_JWT['AUTH_COOKIE']}")
        logger.info(f"🔍 Token from cookie: {'Found' if raw_token else 'Not found'}")
        logger.info(f"🔍 Request origin: {request.META.get('HTTP_ORIGIN', 'None')}")
        logger.info(f"🔍 Request host: {request.META.get('HTTP_HOST', 'None')}")
        
        # If no cookie token, try Authorization header
        if raw_token is None:
            header = self.get_header(request)
            if header is not None:
                raw_token = self.get_raw_token(header)
                logger.debug(f"🔍 Token from Authorization header: {'Found' if raw_token else 'Not found'}")
                # Check if the token is "null" or empty
                if raw_token:
                    try:
                        token_str = raw_token.decode('utf-8') if isinstance(raw_token, bytes) else raw_token
                        if token_str in ['null', '', 'undefined', 'None']:
                            raw_token = None
                            logger.debug("🔍 Token is null/empty, ignoring")
                    except (UnicodeDecodeError, AttributeError):
                        # If decoding fails, try to use it as is
                        pass

        if raw_token is None:
            logger.debug("🔍 No valid token found - authentication failed")
            return None
        
        try:
            # Handle both bytes and string tokens
            if isinstance(raw_token, bytes):
                raw_token = raw_token.decode('utf-8')
            
            validated_token = self.get_validated_token(raw_token)
            # Skip CSRF check for API requests with valid JWT token
            # CSRF is mainly for form-based authentication
            return self.get_user(validated_token), validated_token
        except Exception as e:
            # If token validation fails, return None to allow other auth methods
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Token validation failed: {str(e)}")
            return None

    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[settings.SIMPLE_JWT['USER_ID_CLAIM']]
        except KeyError:
            return None

        # Check cache first
        cache_key = f'user_{user_id}'
        user = cache.get(cache_key)

        if user:
            return user

        # If not in cache, fetch from DB
        user = super().get_user(validated_token)
        
        # Cache the user object for 60 seconds
        # This significantly reduces DB hits for sequential requests
        cache.set(cache_key, user, timeout=60)
        
        return user
        
