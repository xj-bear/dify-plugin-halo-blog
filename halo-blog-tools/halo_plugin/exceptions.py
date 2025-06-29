"""
Custom exceptions for Halo plugin.
"""


class HaloPluginError(Exception):
    """Base exception for Halo plugin errors."""
    pass


class AuthenticationError(HaloPluginError):
    """Raised when authentication fails."""
    pass


class ValidationError(HaloPluginError):
    """Raised when input validation fails."""
    pass


class APIError(HaloPluginError):
    """Raised when API calls fail."""
    
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class ConfigurationError(HaloPluginError):
    """Raised when configuration is invalid."""
    pass


class ResourceNotFoundError(HaloPluginError):
    """Raised when requested resource is not found."""
    pass 