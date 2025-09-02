"""
Helper functions for common operations.
"""

import logging
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
import os

logger = logging.getLogger(__name__)


def resize_image(image, max_width=800, max_height=600, quality=85):
    """
    Resize image while maintaining aspect ratio.
    
    Args:
        image: Django ImageField
        max_width: Maximum width in pixels
        max_height: Maximum height in pixels
        quality: JPEG quality (1-100)
    
    Returns:
        Resized image file
    """
    try:
        # Open image
        img = Image.open(image)
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Calculate new dimensions
        width, height = img.size
        ratio = min(max_width/width, max_height/height)
        
        if ratio < 1:
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Save resized image
        output = ContentFile(b'')
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        return output
        
    except Exception as e:
        logger.error(f"Error resizing image: {str(e)}")
        return image


def generate_unique_filename(original_filename):
    """
    Generate unique filename to avoid conflicts.
    
    Args:
        original_filename: Original filename
    
    Returns:
        Unique filename
    """
    import uuid
    import os
    
    # Get file extension
    ext = os.path.splitext(original_filename)[1]
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{ext}"
    
    return unique_filename


def clean_filename(filename):
    """
    Clean filename by removing special characters.
    
    Args:
        filename: Original filename
    
    Returns:
        Cleaned filename
    """
    import re
    
    # Remove special characters except dots and underscores
    cleaned = re.sub(r'[^\w\-_\.]', '_', filename)
    
    # Remove multiple underscores
    cleaned = re.sub(r'_+', '_', cleaned)
    
    return cleaned


def get_file_size_mb(file):
    """
    Get file size in MB.
    
    Args:
        file: Django file object
    
    Returns:
        File size in MB
    """
    try:
        size_bytes = file.size
        size_mb = size_bytes / (1024 * 1024)
        return round(size_mb, 2)
    except:
        return 0
