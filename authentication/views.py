import os
from django.contrib.auth import authenticate
from django.conf import settings
from django.middleware import csrf
from rest_framework import exceptions as rest_exceptions, response, decorators as rest_decorators, permissions as rest_permissions
from rest_framework_simplejwt import tokens, views as jwt_views, serializers as jwt_serializers, exceptions as jwt_exceptions
from authentication import serializers, models, services


@rest_decorators.api_view(["POST"])
@rest_decorators.permission_classes([])
def loginView(request):
    serializer = serializers.LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data["email"]
    password = serializer.validated_data["password"]

    user = authenticate(email=email, password=password)

    if user is not None:
        tokens = services.get_user_tokens(user)
        res = response.Response()
        
        services.set_auth_cookies(
            res, 
            access_token=tokens["access_token"], 
            refresh_token=tokens["refresh_token"]
        )

        # Serialize user data
        user_serializer = serializers.AccountSerializer(user)
        
        res.data = {
            **tokens,
            "user": user_serializer.data
        }
        res["X-CSRFToken"] = csrf.get_token(request)
        return res
        
    print(f"Authentication failed for email: {email}")
    raise rest_exceptions.AuthenticationFailed(
        "Email or Password is incorrect!")


@rest_decorators.api_view(["POST"])
@rest_decorators.permission_classes([])
def registerView(request):
    serializer = serializers.RegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.save()

    if user is not None:
        # Auto-login after registration
        tokens = services.get_user_tokens(user)
        res = response.Response({
            "message": "User registered successfully!",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone
            },
            **tokens
        }, status=201)
        
        services.set_auth_cookies(
            res, 
            access_token=tokens["access_token"], 
            refresh_token=tokens["refresh_token"]
        )
        
        res["X-CSRFToken"] = csrf.get_token(request)
        return res
    return response.Response({"error": "Failed to create user"}, status=400)


@rest_decorators.api_view(['POST'])
@rest_decorators.permission_classes([rest_permissions.IsAuthenticated])
def logoutView(request):
    try:
        refreshToken = request.COOKIES.get(
            settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
        token = tokens.RefreshToken(refreshToken)
        token.blacklist()

        res = response.Response()
        services.clear_auth_cookies(res)
        res["X-CSRFToken"]=None
        
        return res
    except:
        # Even if token is invalid, we should clear cookies
        res = response.Response()
        services.clear_auth_cookies(res)
        return res


class CookieTokenRefreshSerializer(jwt_serializers.TokenRefreshSerializer):
    refresh = None

    def validate(self, attrs):
        attrs['refresh'] = self.context['request'].COOKIES.get('refresh')
        if attrs['refresh']:
            return super().validate(attrs)
        else:
            raise jwt_exceptions.InvalidToken(
                'No valid token found in cookie \'refresh\'')


class CookieTokenRefreshView(jwt_views.TokenRefreshView):
    serializer_class = CookieTokenRefreshSerializer

    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get("refresh"):
            services.set_auth_cookies(
                response,
                access_token=response.data.get("access"), # SimpleJWT returns 'access' in data
                refresh_token=response.data['refresh']
            )

            del response.data["refresh"]
        response["X-CSRFToken"] = request.COOKIES.get("csrftoken")
        return super().finalize_response(request, response, *args, **kwargs)


@rest_decorators.api_view(["GET"])
@rest_decorators.permission_classes([rest_permissions.IsAuthenticated])
def user(request):
    try:
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return response.Response(
                {"error": "Authentication required"}, 
                status=401
            )
        
        # request.user is already the Account object provided by CustomAuthentication
        # No need to fetch from DB again
        serializer = serializers.AccountSerializer(request.user)
        return response.Response(serializer.data)
        
    except Exception as e:
        return response.Response(
            {"error": "Internal server error"}, 
            status=500
        )


@rest_decorators.api_view(["GET"])
@rest_decorators.permission_classes([rest_permissions.IsAuthenticated])
def checkAuth(request):
    """
    Lightweight endpoint to check if the user is authenticated.
    Returns 200 OK if authenticated, 401 Unauthorized otherwise.
    """
    return response.Response({"isAuthenticated": True}, status=200)


@rest_decorators.api_view(["GET"])
@rest_decorators.permission_classes([])
def get_csrf_token(request):
    """
    Get CSRF token - Django automatically sets csrftoken cookie
    Frontend should read from cookie, not response body
    """
    csrf_token = csrf.get_token(request)
    res = response.Response({"message": "CSRF token set in cookie"})
    res["X-CSRFToken"] = csrf_token
    return res