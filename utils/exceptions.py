"""
Custom exceptions for the application.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class APIException(Exception):
    """Base API exception class."""
    
    def __init__(self, message, status_code=status.HTTP_400_BAD_REQUEST, data=None):
        self.message = message
        self.status_code = status_code
        self.data = data
        super().__init__(self.message)


class ValidationError(APIException):
    """Custom validation error."""
    
    def __init__(self, message="Validation error", data=None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, data)


class NotFoundError(APIException):
    """Custom not found error."""
    
    def __init__(self, message="Not found", data=None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, data)


class UnauthorizedError(APIException):
    """Custom unauthorized error."""
    
    def __init__(self, message="Unauthorized", data=None):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, data)


class ForbiddenError(APIException):
    """Custom forbidden error."""
    
    def __init__(self, message="Forbidden", data=None):
        super().__init__(message, status.HTTP_403_FORBIDDEN, data)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF.
    
    Args:
        exc: Exception instance
        context: Request context
    
    Returns:
        Response: Custom error response
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Log the error
        logger.error(f"API Error: {exc.__class__.__name__} - {str(exc)}")
        
        # Customize error response
        custom_response_data = {
            'success': False,
            'message': str(exc),
            'data': None,
            'error_code': exc.__class__.__name__,
        }
        
        # Add field errors if they exist
        if hasattr(exc, 'detail') and isinstance(exc.detail, dict):
            custom_response_data['data'] = exc.detail
        
        response.data = custom_response_data
    
    return response
