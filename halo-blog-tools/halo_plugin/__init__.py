"""
Halo CMS Integration Plugin for Dify

This plugin provides AI-powered blog management capabilities for Halo CMS,
including article CRUD operations and moment creation.
"""

__version__ = "0.0.1"
__author__ = "jason"

from .exceptions import (
    HaloPluginError,
    AuthenticationError,
    ValidationError,
    APIError,
)

__all__ = [
    "HaloPluginError",
    "AuthenticationError", 
    "ValidationError",
    "APIError",
] 