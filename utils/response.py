"""
Custom response utilities for API responses.
"""

from rest_framework.response import Response
from rest_framework import status


class APIResponse:
    """Custom API response class for consistent responses."""
    
    @staticmethod
    def success(data=None, message="Success", status_code=status.HTTP_200_OK):
        """Return success response."""
        return Response({
            'success': True,
            'message': message,
            'data': data
        }, status=status_code)
    
    @staticmethod
    def error(message="Error", data=None, status_code=status.HTTP_400_BAD_REQUEST):
        """Return error response."""
        return Response({
            'success': False,
            'message': message,
            'data': data
        }, status=status_code)
    
    @staticmethod
    def created(data=None, message="Created successfully"):
        """Return created response."""
        return APIResponse.success(data, message, status.HTTP_201_CREATED)
    
    @staticmethod
    def not_found(message="Not found"):
        """Return not found response."""
        return APIResponse.error(message, status_code=status.HTTP_404_NOT_FOUND)
    
    @staticmethod
    def unauthorized(message="Unauthorized"):
        """Return unauthorized response."""
        return APIResponse.error(message, status_code=status.HTTP_401_UNAUTHORIZED)
    
    @staticmethod
    def forbidden(message="Forbidden"):
        """Return forbidden response."""
        return APIResponse.error(message, status_code=status.HTTP_403_FORBIDDEN)
    
    @staticmethod
    def validation_error(errors, message="Validation error"):
        """Return validation error response."""
        return APIResponse.error(message, errors, status.HTTP_400_BAD_REQUEST)
