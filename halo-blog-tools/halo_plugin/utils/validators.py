"""
Validation utilities for Halo plugin.
"""

import re
from urllib.parse import urlparse
from typing import Optional

from ..exceptions import ValidationError


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid
        
    Raises:
        ValidationError: If URL is invalid
    """
    if not url or not url.strip():
        raise ValidationError("URL cannot be empty")
    
    try:
        result = urlparse(url.strip())
        if not all([result.scheme, result.netloc]):
            raise ValidationError("Invalid URL format")
        
        if result.scheme not in ['http', 'https']:
            raise ValidationError("URL must use HTTP or HTTPS protocol")
        
        return True
    except Exception as e:
        raise ValidationError(f"Invalid URL: {str(e)}")


def validate_token(token: str) -> bool:
    """
    Validate personal access token format.
    
    Args:
        token: Token to validate
        
    Returns:
        True if token is valid
        
    Raises:
        ValidationError: If token is invalid
    """
    if not token or not token.strip():
        raise ValidationError("Personal access token cannot be empty")
    
    # Basic token format validation
    token = token.strip()
    
    # Halo tokens are typically base64-encoded strings
    if len(token) < 10:
        raise ValidationError("Token appears to be too short")
    
    # Check for common token patterns
    if not re.match(r'^[A-Za-z0-9+/=_-]+$', token):
        raise ValidationError("Token contains invalid characters")
    
    return True


def sanitize_content(content: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize content for safe processing.
    
    Args:
        content: Content to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized content
        
    Raises:
        ValidationError: If content is invalid
    """
    if not isinstance(content, str):
        raise ValidationError("Content must be a string")
    
    # Remove null bytes and control characters except common whitespace
    sanitized = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', content)
    
    # Normalize line endings
    sanitized = sanitized.replace('\r\n', '\n').replace('\r', '\n')
    
    # Check length if specified
    if max_length and len(sanitized) > max_length:
        raise ValidationError(f"Content exceeds maximum length of {max_length} characters")
    
    return sanitized


def validate_slug(slug: str) -> bool:
    """
    Validate URL slug format.
    
    Args:
        slug: Slug to validate
        
    Returns:
        True if slug is valid
        
    Raises:
        ValidationError: If slug is invalid
    """
    if not slug:
        return True  # Empty slug is allowed
    
    # URL-safe characters only
    if not re.match(r'^[a-z0-9-]+$', slug):
        raise ValidationError("Slug can only contain lowercase letters, numbers, and hyphens")
    
    # Cannot start or end with hyphen
    if slug.startswith('-') or slug.endswith('-'):
        raise ValidationError("Slug cannot start or end with a hyphen")
    
    # Cannot have consecutive hyphens
    if '--' in slug:
        raise ValidationError("Slug cannot contain consecutive hyphens")
    
    return True


def validate_tags(tags: list) -> bool:
    """
    Validate tags list.
    
    Args:
        tags: List of tags to validate
        
    Returns:
        True if tags are valid
        
    Raises:
        ValidationError: If tags are invalid
    """
    if not isinstance(tags, list):
        raise ValidationError("Tags must be a list")
    
    for tag in tags:
        if not isinstance(tag, str):
            raise ValidationError("Each tag must be a string")
        
        if not tag.strip():
            raise ValidationError("Tags cannot be empty")
        
        if len(tag) > 50:
            raise ValidationError("Tag length cannot exceed 50 characters")
    
    return True 