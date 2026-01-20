"""
Utility functions for file attachments.
"""
import re
import os


def sanitize_filename(filename, max_length=100):
    """
    Sanitize filename by removing special characters and truncating if needed.
    
    Args:
        filename: Original filename
        max_length: Maximum length for filename (default 100)
        
    Returns:
        Sanitized filename
    """
    # Get name and extension
    name, ext = os.path.splitext(filename)
    
    # Remove or replace special characters
    # Keep only alphanumeric, spaces, hyphens, and underscores
    name = re.sub(r'[^\w\s-]', '', name)
    
    # Replace spaces with underscores
    name = re.sub(r'\s+', '_', name)
    
    # Remove leading/trailing underscores and hyphens
    name = name.strip('_-')
    
    # Truncate if too long (leaving room for extension)
    ext_length = len(ext)
    max_name_length = max_length - ext_length
    
    if len(name) > max_name_length:
        name = name[:max_name_length]
    
    # Reconstruct filename
    return f"{name}{ext}".lower()


def format_file_size(size_bytes):
    """
    Format file size in bytes to human-readable format.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Formatted size string (e.g., "2.5 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def get_file_icon_class(content_type):
    """
    Get Bootstrap icon class for file type.
    
    Args:
        content_type: MIME type
        
    Returns:
        Bootstrap icon class name
    """
    icon_mapping = {
        'application/pdf': 'bi-file-earmark-pdf',
        'application/msword': 'bi-file-earmark-word',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'bi-file-earmark-word',
        'application/vnd.ms-excel': 'bi-file-earmark-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'bi-file-earmark-excel',
        'text/plain': 'bi-file-earmark-text',
        'image/jpeg': 'bi-file-earmark-image',
        'image/png': 'bi-file-earmark-image',
    }
    
    return icon_mapping.get(content_type, 'bi-file-earmark')
