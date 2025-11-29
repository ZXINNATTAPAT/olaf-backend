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
    import sys
    
    logger = logging.getLogger(__name__)
    
    # Force INFO level logging and ensure it goes to console
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    # Also print to stdout for immediate visibility
    print("=" * 50, file=sys.stdout)
    print("🍪 START: set_auth_cookies() called", file=sys.stdout)
    print("=" * 50, file=sys.stdout)
    sys.stdout.flush()
    
    logger.info("=" * 50)
    logger.info("🍪 START: set_auth_cookies() called")
    logger.info("=" * 50)
    
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
    
    logger.info(f"🍪 Cookie domain set to: {cookie_domain} (None = use request domain)")
    
    # Determine SameSite value - use None for cross-origin (production), Lax for same-origin (dev)
    # Try without SameSite attribute to see if it helps with cookie sending
    samesite = None  # Don't set SameSite attribute - let browser handle it
    secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE']
    
    # Log cookie settings for debugging
    logger.info(f"🍪 Cookie Settings - Domain: {cookie_domain}, SameSite: {samesite} (None = not set), Secure: {secure}")
    logger.info(f"🍪 Access token length: {len(access_token) if access_token else 0}")
    logger.info(f"🍪 Refresh token length: {len(refresh_token) if refresh_token else 0}")
    logger.info(f"🍪 Cookie names - Access: {settings.SIMPLE_JWT['AUTH_COOKIE']}, Refresh: {settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH']}")
    
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
        logger.info(f"✅ Set access token cookie: {settings.SIMPLE_JWT['AUTH_COOKIE']}")
        print(f"✅ Set access token cookie: {settings.SIMPLE_JWT['AUTH_COOKIE']}", file=sys.stdout)
        sys.stdout.flush()
    except Exception as e:
        logger.error(f"❌ Failed to set access token cookie: {str(e)}", exc_info=True)
        print(f"❌ Failed to set access token cookie: {str(e)}", file=sys.stdout)
        sys.stdout.flush()

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
            logger.info(f"✅ Set refresh token cookie: {settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH']}")
            print(f"✅ Set refresh token cookie: {settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH']}", file=sys.stdout)
            sys.stdout.flush()
        except Exception as e:
            logger.error(f"❌ Failed to set refresh token cookie: {str(e)}", exc_info=True)
            print(f"❌ Failed to set refresh token cookie: {str(e)}", file=sys.stdout)
            sys.stdout.flush()
    
    # Log response headers for debugging (note: Set-Cookie won't show in dict(response.items()))
    # But we can check if cookies are in the response
    logger.info(f"🍪 Response status: {response.status_code}")
    logger.info(f"🍪 Response has cookies attribute: {hasattr(response, 'cookies')}")
    
    # Try to verify cookies were set by checking response._headers (internal Django structure)
    try:
        # Django stores Set-Cookie headers in response._headers
        if hasattr(response, '_headers'):
            set_cookie_headers = [h for h in response._headers.values() if h[0].lower() == 'set-cookie']
            logger.info(f"🍪 Number of Set-Cookie headers: {len(set_cookie_headers)}")
            for header in set_cookie_headers:
                cookie_name = header[1].split('=')[0] if '=' in header[1] else 'unknown'
                logger.info(f"🍪 Set-Cookie header found: {cookie_name}")
    except Exception as e:
        logger.warning(f"🍪 Could not verify Set-Cookie headers: {str(e)}")
    
    logger.info("=" * 50)
    logger.info("🍪 END: set_auth_cookies() completed")
    logger.info("=" * 50)
    
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
