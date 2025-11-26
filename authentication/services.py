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
    Optimized for Railway deployment with proper domain and SameSite settings.
    """
    # Get cookie domain from environment or use None (which works for same-origin)
    cookie_domain = os.getenv('COOKIE_DOMAIN', None)
    
    # For Railway, we might need to set domain to None or use the actual domain
    # None works best for cross-origin requests when using SameSite=None
    if cookie_domain and cookie_domain.strip():
        cookie_domain = cookie_domain.strip()
    else:
        cookie_domain = None
    
    # Determine SameSite value - use None for cross-origin (production), Lax for same-origin (dev)
    samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
    
    # Set access token cookie
    response.set_cookie(
        key=settings.SIMPLE_JWT['AUTH_COOKIE'],
        value=access_token,
        max_age=int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
        expires=None,  # Use max_age instead for better compatibility
        secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
        samesite=samesite,
        domain=cookie_domain,
        path='/'
    )

    # Set refresh token cookie if provided
    if refresh_token:
        response.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
            value=refresh_token,
            max_age=int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()),
            expires=None,  # Use max_age instead
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            samesite=samesite,
            domain=cookie_domain,
            path='/'
        )
    
    return response

def clear_auth_cookies(response):
    """
    Clear authentication cookies from the response.
    """
    cookie_domain = os.getenv('COOKIE_DOMAIN', None)
    if cookie_domain and cookie_domain.strip():
        cookie_domain = cookie_domain.strip()
    else:
        cookie_domain = None
    
    # Clear auth cookies
    response.delete_cookie(
        settings.SIMPLE_JWT['AUTH_COOKIE'],
        path='/',
        domain=cookie_domain,
        samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
    )
    response.delete_cookie(
        settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
        path='/',
        domain=cookie_domain,
        samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
    )
    
    # Clear CSRF cookies
    response.delete_cookie("csrftoken", path='/', domain=cookie_domain)
    response.delete_cookie("X-CSRFToken", path='/', domain=cookie_domain)
    
    return response
