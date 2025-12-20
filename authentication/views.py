import os
from django.contrib.auth import authenticate
from django.conf import settings
from django.middleware import csrf
from rest_framework import exceptions as rest_exceptions, response, decorators as rest_decorators, permissions as rest_permissions, status
from rest_framework_simplejwt import tokens, views as jwt_views, serializers as jwt_serializers, exceptions as jwt_exceptions
from authentication import serializers, models, services
import logging

logger = logging.getLogger(__name__)


@rest_decorators.api_view(["POST"])
@rest_decorators.permission_classes([])
def loginView(request):
    """
    User login endpoint.
    Returns JWT tokens in HTTP-only cookies and user data in response body.
    """
    try:
        serializer = serializers.LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = authenticate(request=request, email=email, password=password)

        if user is None or not user.is_active:
            logger.warning(f"Login failed for email: {email}")
            return response.Response(
                {"error": "Email or Password is incorrect!"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Generate tokens
        token_data = services.get_user_tokens(user)
        logger.info(f"🔑 Generated tokens for user {user.email} - Access: {len(token_data.get('access_token', ''))}, Refresh: {len(token_data.get('refresh_token', ''))}")
        
        # Create response with user data
        user_serializer = serializers.AccountSerializer(user)
        res = response.Response({
            "message": "Login successful",
            "user": user_serializer.data
        }, status=status.HTTP_200_OK)
        
        # Set authentication cookies
        logger.info(f"🍪 About to set cookies for user {user.email}")
        services.set_auth_cookies(
            res, 
            access_token=token_data["access_token"], 
            refresh_token=token_data["refresh_token"]
        )
        logger.info(f"🍪 Finished setting cookies for user {user.email}")

        # Set CSRF token in header
        csrf_token = csrf.get_token(request)
        res["X-CSRFToken"] = csrf_token
        
        # Explicitly set CORS headers (django-cors-headers should do this, but ensure it's set)
        origin = request.META.get('HTTP_ORIGIN')
        if origin and origin in settings.CORS_ALLOWED_ORIGINS:
            res["Access-Control-Allow-Origin"] = origin
            res["Access-Control-Allow-Credentials"] = "true"
        
        # Log response headers for debugging (including cookies)
        # Note: Set-Cookie headers won't appear in dict(res.items()) but will be in final response
        logger.info(f"Login response headers: {dict(res.items())}")
        logger.info(f"Login response cookies set: access={bool(token_data.get('access_token'))}, refresh={bool(token_data.get('refresh_token'))}")
        logger.info(f"Origin: {origin}, CORS headers set: {bool(origin and origin in settings.CORS_ALLOWED_ORIGINS)}")
        
        # Verify cookies are in response (they should be set by services.set_auth_cookies)
        # We can't directly check Set-Cookie in response object, but we log that we called set_cookie
        logger.info(f"User {user.email} logged in successfully")
        
        return res
        
    except rest_exceptions.ValidationError as e:
        return response.Response(
            {"error": "Invalid input", "details": e.detail},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        return response.Response(
            {"error": "An error occurred during login. Please try again."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@rest_decorators.api_view(["POST"])
@rest_decorators.permission_classes([])
def registerView(request):
    """
    User registration endpoint.
    Creates a new user and automatically logs them in.
    """
    try:
        serializer = serializers.RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        if user is None:
            return response.Response(
                {"error": "Failed to create user"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Auto-login after registration
        token_data = services.get_user_tokens(user)
        user_serializer = serializers.AccountSerializer(user)
        
        res = response.Response({
            "message": "User registered successfully!",
            "user": user_serializer.data
        }, status=status.HTTP_201_CREATED)
        
        # Set authentication cookies
        services.set_auth_cookies(
            res, 
            access_token=token_data["access_token"], 
            refresh_token=token_data["refresh_token"]
        )
        
        # Set CSRF token
        csrf_token = csrf.get_token(request)
        res["X-CSRFToken"] = csrf_token
        
        # Explicitly set CORS headers (django-cors-headers should do this, but ensure it's set)
        origin = request.META.get('HTTP_ORIGIN')
        if origin and origin in settings.CORS_ALLOWED_ORIGINS:
            res["Access-Control-Allow-Origin"] = origin
            res["Access-Control-Allow-Credentials"] = "true"
        
        # Log response headers for debugging
        logger.info(f"Register response headers: {dict(res.items())}")
        logger.info(f"Register response cookies set: access={bool(token_data.get('access_token'))}, refresh={bool(token_data.get('refresh_token'))}")
        logger.info(f"Origin: {origin}, CORS headers set: {bool(origin and origin in settings.CORS_ALLOWED_ORIGINS)}")
        logger.info(f"User {user.email} registered successfully")
        return res
        
    except rest_exceptions.ValidationError as e:
        return response.Response(
            {"error": "Validation failed", "details": e.detail},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        return response.Response(
            {"error": "An error occurred during registration. Please try again."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@rest_decorators.api_view(['POST'])
@rest_decorators.permission_classes([rest_permissions.IsAuthenticated])
def logoutView(request):
    """
    User logout endpoint.
    Blacklists the refresh token and clears authentication cookies.
    """
    try:
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
        
        if refresh_token:
            try:
                token = tokens.RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                # Token might be invalid or already blacklisted, continue anyway
                logger.warning(f"Token blacklist error: {str(e)}")

        res = response.Response(
            {"message": "Logged out successfully"},
            status=status.HTTP_200_OK
        )
        services.clear_auth_cookies(res)
        
        # Set CORS headers
        origin = request.META.get('HTTP_ORIGIN')
        if origin and origin in settings.CORS_ALLOWED_ORIGINS:
            res["Access-Control-Allow-Origin"] = origin
            res["Access-Control-Allow-Credentials"] = "true"
        
        logger.info(f"User {request.user.email if request.user.is_authenticated else 'Unknown'} logged out")
        return res
        
    except Exception as e:
        # Even if there's an error, clear cookies
        logger.error(f"Logout error: {str(e)}", exc_info=True)
        res = response.Response(
            {"message": "Logged out (some errors occurred)"},
            status=status.HTTP_200_OK
        )
        services.clear_auth_cookies(res)
        return res


class CookieTokenRefreshSerializer(jwt_serializers.TokenRefreshSerializer):
    refresh = None

    def validate(self, attrs):
        # Try to get refresh token from multiple sources:
        # 1. Request body (if sent explicitly)
        # 2. Cookie (preferred for security)
        # 3. Authorization header (fallback)
        request = self.context['request']
        
        # Log cookies for debugging - use INFO level for visibility
        all_cookies = dict(request.COOKIES)
        logger.info(f"🔄 Refresh token request - Cookies received: {list(all_cookies.keys())}")
        logger.info(f"🔄 All cookies: {all_cookies}")
        logger.info(f"🔄 Looking for cookie: {settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH']}")
        logger.info(f"🔄 Request origin: {request.META.get('HTTP_ORIGIN', 'None')}")
        logger.info(f"🔄 Request host: {request.META.get('HTTP_HOST', 'None')}")
        
        # Check request body first
        if 'refresh' in request.data:
            attrs['refresh'] = request.data['refresh']
            logger.debug("🔄 Refresh token from request body")
        # Check cookie
        elif request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH']):
            attrs['refresh'] = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
            logger.debug("🔄 Refresh token from cookie")
        # Check Authorization header as fallback
        else:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('Bearer '):
                attrs['refresh'] = auth_header.split(' ')[1]
                logger.debug("🔄 Refresh token from Authorization header")
        
        if attrs.get('refresh'):
            return super().validate(attrs)
        else:
            logger.warning(f"❌ No refresh token found. Cookies: {list(all_cookies.keys())}")
            raise jwt_exceptions.InvalidToken(
                'No valid refresh token found. Please provide refresh token in cookie, body, or Authorization header.')


class CookieTokenRefreshView(jwt_views.TokenRefreshView):
    serializer_class = CookieTokenRefreshSerializer
    permission_classes = []  # Allow unauthenticated access for token refresh

    def finalize_response(self, request, response, *args, **kwargs):
        try:
            # Only set cookies if response is successful (200 OK)
            if response.status_code == 200 and response.data.get("access"):
                # Set cookies with new tokens
                refresh_token = response.data.get("refresh")
                if refresh_token:
                    services.set_auth_cookies(
                        response,
                        access_token=response.data.get("access"),
                        refresh_token=refresh_token
                    )
                    del response.data["refresh"]
                else:
                    # If no new refresh token, just update access token
                    services.set_auth_cookies(
                        response,
                        access_token=response.data.get("access"),
                        refresh_token=None
                    )
                
                # Update CSRF token
                csrf_token = csrf.get_token(request)
                response["X-CSRFToken"] = csrf_token
            
            return super().finalize_response(request, response, *args, **kwargs)
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}", exc_info=True)
            return super().finalize_response(request, response, *args, **kwargs)


@rest_decorators.api_view(["GET"])
@rest_decorators.permission_classes([rest_permissions.IsAuthenticated])
def user(request):
    """
    Get current authenticated user profile.
    """
    try:
        if not request.user or not request.user.is_authenticated:
            return response.Response(
                {"error": "Authentication required"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = serializers.AccountSerializer(request.user)
        return response.Response(serializer.data, status=status.HTTP_200_OK)
        
    except (jwt_exceptions.InvalidToken, jwt_exceptions.AuthenticationFailed) as e:
        logger.warning(f"Authentication failed: {str(e)}")
        return response.Response(
            {"error": "Invalid token", "code": "token_not_valid"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        logger.error(f"Get user error: {str(e)}", exc_info=True)
        return response.Response(
            {"error": "Internal server error"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@rest_decorators.api_view(["GET"])
@rest_decorators.permission_classes([rest_permissions.IsAuthenticated])
def checkAuth(request):
    """
    Lightweight endpoint to check if the user is authenticated.
    Returns 200 OK if authenticated, 401 Unauthorized otherwise.
    """
    return response.Response(
        {"isAuthenticated": True, "user_id": request.user.id},
        status=status.HTTP_200_OK
    )


@rest_decorators.api_view(["GET"])
@rest_decorators.permission_classes([])
def get_csrf_token(request):
    """
    Get CSRF token endpoint.
    Django automatically sets csrftoken cookie.
    Also returns token in X-CSRFToken header for convenience.
    """
    try:
        csrf_token = csrf.get_token(request)
        res = response.Response({
            "message": "CSRF token available",
            "csrfToken": csrf_token
        }, status=status.HTTP_200_OK)
        res["X-CSRFToken"] = csrf_token
        
        # Set CORS headers
        origin = request.META.get('HTTP_ORIGIN')
        if origin and origin in settings.CORS_ALLOWED_ORIGINS:
            res["Access-Control-Allow-Origin"] = origin
            res["Access-Control-Allow-Credentials"] = "true"
        
        return res
    except Exception as e:
        logger.error(f"CSRF token error: {str(e)}", exc_info=True)
        return response.Response(
            {"error": "Failed to get CSRF token"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@rest_decorators.api_view(["GET", "POST"])
@rest_decorators.permission_classes([])
def test_cookies(request):
    """
    Test endpoint to verify cookie setting works.
    Sets a test cookie and returns cookie information.
    """
    try:
        # Set a test cookie
        test_cookie_value = "test_cookie_value_12345"
        res = response.Response({
            "message": "Test cookie endpoint",
            "test_cookie_set": True,
            "cookies_received": dict(request.COOKIES),
            "origin": request.META.get('HTTP_ORIGIN'),
            "settings": {
                "CORS_ALLOWED_ORIGINS": settings.CORS_ALLOWED_ORIGINS,
                "CORS_ALLOW_CREDENTIALS": settings.CORS_ALLOW_CREDENTIALS,
                "AUTH_COOKIE_SAMESITE": settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                "AUTH_COOKIE_SECURE": settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                "DEBUG": settings.DEBUG,
            }
        }, status=status.HTTP_200_OK)
        
        # Set test cookie
        res.set_cookie(
            'test_cookie',
            test_cookie_value,
            max_age=3600,
            httponly=False,  # Allow JS to read for testing
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
            path='/'
        )
        
        # Set CORS headers
        origin = request.META.get('HTTP_ORIGIN')
        if origin and origin in settings.CORS_ALLOWED_ORIGINS:
            res["Access-Control-Allow-Origin"] = origin
            res["Access-Control-Allow-Credentials"] = "true"
        elif not origin:
            # If no origin header, allow all (for testing)
            res["Access-Control-Allow-Origin"] = "*"
        
        logger.info(f"Test cookie endpoint - Origin: {origin}, Cookies: {dict(request.COOKIES)}")
        return res
    except Exception as e:
        logger.error(f"Test cookie error: {str(e)}", exc_info=True)
        return response.Response(
            {"error": f"Test cookie failed: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )