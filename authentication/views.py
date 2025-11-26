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
        
        # Create response with user data
        user_serializer = serializers.AccountSerializer(user)
        res = response.Response({
            "message": "Login successful",
            "user": user_serializer.data
        }, status=status.HTTP_200_OK)
        
        # Set authentication cookies
        services.set_auth_cookies(
            res, 
            access_token=token_data["access_token"], 
            refresh_token=token_data["refresh_token"]
        )

        # Set CSRF token in header
        csrf_token = csrf.get_token(request)
        res["X-CSRFToken"] = csrf_token
        
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
        attrs['refresh'] = self.context['request'].COOKIES.get(
            settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH']
        )
        if attrs['refresh']:
            return super().validate(attrs)
        else:
            raise jwt_exceptions.InvalidToken(
                'No valid refresh token found in cookie')


class CookieTokenRefreshView(jwt_views.TokenRefreshView):
    serializer_class = CookieTokenRefreshSerializer

    def finalize_response(self, request, response, *args, **kwargs):
        try:
            if response.data.get("refresh"):
                services.set_auth_cookies(
                    response,
                    access_token=response.data.get("access"),
                    refresh_token=response.data['refresh']
                )
                del response.data["refresh"]
            
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
        return res
    except Exception as e:
        logger.error(f"CSRF token error: {str(e)}", exc_info=True)
        return response.Response(
            {"error": "Failed to get CSRF token"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )