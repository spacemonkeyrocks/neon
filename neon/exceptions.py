class NeonError(Exception):
    """Base exception for all neon errors."""
    pass

class ThemeNotFoundError(NeonError):
    """Raised when a theme file cannot be found."""
    pass

class ConfigError(NeonError):
    """Raised when configuration is invalid."""
    pass