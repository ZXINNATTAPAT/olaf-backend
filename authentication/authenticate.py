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
        
        raw_token = None
        token_source = None
        
        # Log request details for debugging
        all_cookies = dict(request.COOKIES)
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        logger.info(f"🔍 Authentication attempt - Origin: {request.META.get('HTTP_ORIGIN', 'None')}")
        logger.info(f"🔍 Cookies received: {list(all_cookies.keys())}")
        logger.info(f"🔍 Authorization header present: {bool(auth_header)}")
        
        # Try Authorization header FIRST (better for cross-site requests)
        header = self.get_header(request)
        if header is not None:
            try:
                raw_token = self.get_raw_token(header)
                if raw_token:
                    # Check if the token is "null" or empty
                    token_str = raw_token.decode('utf-8') if isinstance(raw_token, bytes) else raw_token
                    if token_str not in ['null', '', 'undefined', 'None']:
                        token_source = 'Authorization header'
                        logger.info(f"🔍 ✅ Token found in Authorization header")
                    else:
                        raw_token = None
                        logger.debug("🔍 Token in header is null/empty, ignoring")
            except (UnicodeDecodeError, AttributeError) as e:
                logger.debug(f"🔍 Error decoding token from header: {str(e)}")
                raw_token = None
        
        # Fallback to cookies if no Authorization header token
        if raw_token is None:
            cookie_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])
            if cookie_token:
                raw_token = cookie_token
                token_source = 'Cookie'
                logger.info(f"🔍 ✅ Token found in cookie: {settings.SIMPLE_JWT['AUTH_COOKIE']}")
            else:
                logger.info(f"🔍 ❌ No token in cookie: {settings.SIMPLE_JWT['AUTH_COOKIE']}")

        if raw_token is None:
            logger.warning("🔍 ❌ No valid token found in Authorization header or cookies")
            return None
        
        try:
            # Handle both bytes and string tokens
            if isinstance(raw_token, bytes):
                raw_token = raw_token.decode('utf-8')
            
            logger.info(f"🔍 Validating token from {token_source}...")
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            logger.info(f"🔍 ✅ Authentication successful for user: {user.email if hasattr(user, 'email') else user.id}")
            # Skip CSRF check for API requests with valid JWT token
            # CSRF is mainly for form-based authentication
            return user, validated_token
        except Exception as e:
            # If token validation fails, return None to allow other auth methods
            logger.warning(f"🔍 ❌ Token validation failed from {token_source}: {str(e)}")
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

        try:
            # If not in cache, fetch from DB
            user = super().get_user(validated_token)
            
            # Cache the user object for 60 seconds
            # This significantly reduces DB hits for sequential requests
            cache.set(cache_key, user, timeout=60)
            
            return user
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting user from token: {str(e)}")
            # Raise AuthenticationFailed to result in 401 instead of 500
            from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
            raise AuthenticationFailed("User not found or invalid token", code="user_not_found")
        
