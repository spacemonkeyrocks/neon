class NeonError(Exception):
    """Base exception for all neon errors."""
    pass

class NeonThemeNotFoundError(NeonError):
    """Raised when a theme file cannot be found."""
    pass

class NeonConfigError(NeonError):
    """Raised when configuration is invalid."""
    pass