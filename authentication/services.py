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
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Get cookie domain from environment or use None
    # IMPORTANT: For cross-origin requests (localhost:3000 -> localhost:8000):
    # - Setting domain=None means cookies are set for the exact domain that set them (localhost:8000)
    # - With SameSite=None and withCredentials:true, cookies will be sent from localhost:3000 to localhost:8000
    # - Setting domain='localhost' may cause issues because browser treats it differently
    cookie_domain = os.getenv('COOKIE_DOMAIN', None)
    
    # For cross-origin requests with SameSite=None:
    # - domain=None is the correct setting - cookies will be sent with withCredentials:true
    # - The browser will send cookies from localhost:3000 to localhost:8000 automatically
    if cookie_domain and cookie_domain.strip():
        cookie_domain = cookie_domain.strip()
    else:
        # Use None for cross-origin - cookies will be sent with withCredentials:true and SameSite=None
        cookie_domain = None
    
    # Determine SameSite value - use None for cross-origin (production), Lax for same-origin (dev)
    # Try without SameSite attribute to see if it helps with cookie sending
    samesite = None  # Don't set SameSite attribute - let browser handle it
    secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE']
    
    # Set access token cookie
    try:
        response.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE'],
            value=access_token,
            max_age=int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
            expires=None,  # Use max_age instead for better compatibility
            secure=secure,
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            samesite=samesite,
            domain=cookie_domain,
            path='/'
        )
    except Exception as e:
        logger.error(f"Failed to set access token cookie: {str(e)}", exc_info=True)

    # Set refresh token cookie if provided
    if refresh_token:
        try:
            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
                value=refresh_token,
                max_age=int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()),
                expires=None,  # Use max_age instead
                secure=secure,
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=samesite,
                domain=cookie_domain,
                path='/'
            )
        except Exception as e:
            logger.error(f"Failed to set refresh token cookie: {str(e)}", exc_info=True)
    
    return response

def clear_auth_cookies(response):
    """
    Clear authentication cookies from the response.
    """
    cookie_domain = os.getenv('COOKIE_DOMAIN', None)
    if cookie_domain and cookie_domain.strip():
        cookie_domain = cookie_domain.strip()
    else:
        # Use None to match set_auth_cookies
        cookie_domain = None
    
    # Clear auth cookies (don't set SameSite when deleting)
    response.delete_cookie(
        settings.SIMPLE_JWT['AUTH_COOKIE'],
        path='/',
        domain=cookie_domain,
        samesite=None  # Don't set SameSite when deleting
    )
    response.delete_cookie(
        settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
        path='/',
        domain=cookie_domain,
        samesite=None  # Don't set SameSite when deleting
    )
    
    # Clear CSRF cookies (don't set SameSite when deleting)
    response.delete_cookie("csrftoken", path='/', domain=cookie_domain, samesite=None)
    response.delete_cookie("X-CSRFToken", path='/', domain=cookie_domain, samesite=None)
    
    return response
