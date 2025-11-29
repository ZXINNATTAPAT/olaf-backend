"""
Django-Bolt API routes for authentication endpoints.
"""
from django_bolt import BoltAPI
from django_bolt.serializers import Serializer
from django_bolt.responses import JSON, Response
from typing import Annotated, Optional
from msgspec import Meta
from django.contrib.auth import authenticate
from django.conf import settings
from django.middleware import csrf
from rest_framework_simplejwt import tokens
from asgiref.sync import sync_to_async
from . import models, services, serializers as auth_serializers
import logging

logger = logging.getLogger(__name__)

# Wrap synchronous functions for async use
async_authenticate = sync_to_async(authenticate, thread_sensitive=False)

# Initialize Bolt API with OpenAPI/Swagger configuration
from django_bolt import OpenAPIConfig

api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="Olaf Backend API - Authentication",
        version="1.0.0",
        description="Authentication endpoints for Olaf platform",
    ),
)

# Serializers
class LoginSerializer(Serializer):
    email: str
    password: str

class RegistrationSerializer(Serializer):
    username: Annotated[str, Meta(min_length=3, max_length=150)]
    email: str
    password: Annotated[str, Meta(min_length=8)]
    password2: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None

# API Routes
@api.post("/login")
async def login(data: LoginSerializer):
    """User login endpoint"""
    try:
        # Use async_authenticate wrapper
        user = await async_authenticate(email=data.email, password=data.password)
        
        if user is None or not user.is_active:
            logger.warning(f"Login failed for email: {data.email}")
            return JSON(
                {"error": "Email or Password is incorrect!"},
                status_code=401
            )
        
        # Generate tokens (synchronous function, wrap it)
        token_data = await sync_to_async(services.get_user_tokens)(user)
        logger.info(f"🔑 Generated tokens for user {user.email}")
        
        # Get user data (serializer is synchronous)
        def get_user_data():
            serializer = auth_serializers.AccountSerializer(user)
            return serializer.data
        
        user_data = await sync_to_async(get_user_data)()
        
        # Create response
        response_data = {
            "message": "Login successful",
            "user": user_data
        }
        
        # Note: Cookie setting will need to be handled in middleware or response handler
        # Django-Bolt may need custom response handling for cookies
        
        return response_data
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        return JSON(
            {"error": "An error occurred during login. Please try again."},
            status_code=500
        )

@api.post("/register")
async def register(data: RegistrationSerializer):
    """User registration endpoint"""
    try:
        # Validate passwords match
        if data.password != data.password2:
            return JSON(
                {"error": "Passwords do not match"},
                status_code=400
            )
        
        # Create user (serializer operations are synchronous)
        data_dict = data.to_dict()
        
        def create_user():
            serializer = auth_serializers.RegistrationSerializer(data=data_dict)
            if not serializer.is_valid():
                return None, serializer.errors
            user = serializer.save()
            return user, None
        
        user, errors = await sync_to_async(create_user)()
        
        if user is None:
            return JSON(
                {"error": "Validation failed", "details": errors},
                status_code=400
            )
        
        # Auto-login after registration
        token_data = await sync_to_async(services.get_user_tokens)(user)
        
        def get_user_data():
            serializer = auth_serializers.AccountSerializer(user)
            return serializer.data
        
        user_data = await sync_to_async(get_user_data)()
        
        response_data = {
            "message": "User registered successfully!",
            "user": user_data
        }
        
        return response_data
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        return JSON(
            {"error": "An error occurred during registration. Please try again."},
            status_code=500
        )

@api.post("/logout")
async def logout():
    """User logout endpoint"""
    # TODO: Implement authentication guard
    # TODO: Blacklist refresh token
    # TODO: Clear cookies
    
    return {"message": "Logged out successfully"}

@api.get("/user")
async def get_user():
    """Get current authenticated user profile"""
    # TODO: Implement authentication guard
    # TODO: Return user data
    
    return JSON(
        {"error": "Authentication required"},
        status_code=401
    )

@api.get("/check")
async def check_auth():
    """Check if user is authenticated"""
    # TODO: Implement authentication guard
    
    return JSON(
        {"error": "Authentication required"},
        status_code=401
    )

@api.get("/csrf")
async def get_csrf_token():
    """Get CSRF token"""
    # TODO: Implement CSRF token generation
    
    return {
        "message": "CSRF token available",
        "csrfToken": "token_here"  # TODO: Generate actual token
    }

@api.post("/refresh-token")
async def refresh_token(request):
    """Refresh JWT access token using refresh token"""
    from rest_framework_simplejwt import tokens, exceptions as jwt_exceptions
    from django.conf import settings
    
    try:
        # Get refresh token from cookie or request body
        refresh_token_value = None
        
        # Try to get from request body (BoltAPI may need to extract from request)
        # For now, we'll need to get it from the request object
        # Note: BoltAPI handlers receive request as parameter if needed
        if hasattr(request, 'COOKIES'):
            refresh_token_value = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
        
        if not refresh_token_value:
            return JSON(
                {"error": "No valid refresh token found. Please provide refresh token in cookie."},
                status_code=401
            )
        
        # Validate and refresh token
        def refresh_token_sync():
            try:
                refresh = tokens.RefreshToken(refresh_token_value)
                access_token = str(refresh.access_token)
                # Optionally rotate refresh token
                new_refresh_token = str(refresh)
                return access_token, new_refresh_token
            except Exception as e:
                raise jwt_exceptions.InvalidToken(f"Invalid refresh token: {str(e)}")
        
        access_token, new_refresh_token = await sync_to_async(refresh_token_sync)()
        
        # Return new tokens
        # Note: Cookie setting will need to be handled in middleware or response handler
        return {
            "access": access_token,
            "refresh": new_refresh_token,
            "message": "Token refreshed successfully"
        }
        
    except jwt_exceptions.InvalidToken as e:
        return JSON(
            {"error": str(e)},
            status_code=401
        )
    except Exception as e:
        logger.error(f"Refresh token error: {str(e)}", exc_info=True)
        return JSON(
            {"error": "An error occurred during token refresh. Please try again."},
            status_code=500
        )

