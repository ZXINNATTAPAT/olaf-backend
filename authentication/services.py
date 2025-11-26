from django.conf import settings
from rest_framework_simplejwt import tokens
import os

def get_user_tokens(user):
    """
    Generate access and refresh tokens for a user.
    """
    refresh = tokens.RefreshToken.for_user(user)
    return {
        "refresh_token": str(refresh),
        "access_token": str(refresh.access_token)
    }

def set_auth_cookies(response, access_token, refresh_token=None):
    """
    Set authentication cookies on the response.
    """
    cookie_domain = None
    if not settings.DEBUG:
        cookie_domain = os.getenv('COOKIE_DOMAIN', None)
    
    # Set access token cookie
    response.set_cookie(
        key=settings.SIMPLE_JWT['AUTH_COOKIE'],
        value=access_token,
        expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
        secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
        samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
        domain=cookie_domain
    )

    # Set refresh token cookie if provided
    if refresh_token:
        response.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
            value=refresh_token,
            expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
            domain=cookie_domain
        )
    
    return response

def clear_auth_cookies(response):
    """
    Clear authentication cookies from the response.
    """
    response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
    response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
    response.delete_cookie("X-CSRFToken")
    response.delete_cookie("csrftoken")
    return response
