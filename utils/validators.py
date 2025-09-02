"""
Custom validators for models and serializers.
"""

import re
from django.core.exceptions import ValidationError


def validate_phone_number(value):
    """Validate phone number format."""
    # Thai phone number pattern
    phone_pattern = r'^(\+66|0)[0-9]{8,9}$'
    if not re.match(phone_pattern, value):
        raise ValidationError('Invalid phone number format. Use Thai phone number format.')
    return value


def validate_password_strength(value):
    """Validate password strength."""
    if len(value) < 8:
        raise ValidationError('Password must be at least 8 characters long.')
    
    if not re.search(r'[A-Z]', value):
        raise ValidationError('Password must contain at least one uppercase letter.')
    
    if not re.search(r'[a-z]', value):
        raise ValidationError('Password must contain at least one lowercase letter.')
    
    if not re.search(r'[0-9]', value):
        raise ValidationError('Password must contain at least one number.')
    
    return value


def validate_username(value):
    """Validate username format."""
    if len(value) < 3:
        raise ValidationError('Username must be at least 3 characters long.')
    
    if not re.match(r'^[a-zA-Z0-9_]+$', value):
        raise ValidationError('Username can only contain letters, numbers, and underscores.')
    
    return value
