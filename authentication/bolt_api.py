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
from . import models, services, serializers as auth_serializers
import logging

logger = logging.getLogger(__name__)

# Initialize Bolt API
api = BoltAPI()

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
        user = authenticate(email=data.email, password=data.password)
        
        if user is None or not user.is_active:
            logger.warning(f"Login failed for email: {data.email}")
            return JSON(
                {"error": "Email or Password is incorrect!"},
                status_code=401
            )
        
        # Generate tokens
        token_data = services.get_user_tokens(user)
        logger.info(f"🔑 Generated tokens for user {user.email}")
        
        # Get user data
        user_serializer = auth_serializers.AccountSerializer(user)
        
        # Create response
        response_data = {
            "message": "Login successful",
            "user": user_serializer.data
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
        
        # Create user
        serializer = auth_serializers.RegistrationSerializer(data=data.to_dict())
        if not serializer.is_valid():
            return JSON(
                {"error": "Validation failed", "details": serializer.errors},
                status_code=400
            )
        
        user = serializer.save()
        
        if user is None:
            return JSON(
                {"error": "Failed to create user"},
                status_code=400
            )
        
        # Auto-login after registration
        token_data = services.get_user_tokens(user)
        user_serializer = auth_serializers.AccountSerializer(user)
        
        response_data = {
            "message": "User registered successfully!",
            "user": user_serializer.data
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

