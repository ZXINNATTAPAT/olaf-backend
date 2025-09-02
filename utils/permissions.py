"""
Custom permissions for the application.
"""

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners or admins to access an object.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin users have full access
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Owners have full access
        return obj.user == request.user


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read-only access for unauthenticated users,
    and full access for authenticated users.
    """
    
    def has_permission(self, request, view):
        # Allow read-only access for unauthenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Require authentication for write operations
        return request.user and request.user.is_authenticated


class IsPostOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission for post-related operations.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the post owner
        return obj.user == request.user


class IsCommentOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission for comment-related operations.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the comment owner
        return obj.user == request.user
