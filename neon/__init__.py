"""
neon v3.0 - Rich-based ArgumentParser with beautiful formatting.

A powerful, simplified ArgumentParser formatter using Rich for beautiful
colored output, table-based layouts, and dynamic text highlighting.
"""

from .__version__ import __version__
from .parser import RichArgumentParser, CustomColoredArgumentParser
from .config import Config
from .theme import ThemeManager
from .formatter import RichFormatter
from .highlighting import SmartHighlighter

__author__ = "Space Monkey Rocks"
__email__ = "info@spacemonkey.rocks"
__license__ = "MIT"
__title__ = "neon"
__url__ = "https://github.com/SpaceMonkeyRocks/neon"
__copyright__ = "Copyright (c) 2023 Space Monkey Rocks"
__description__ = "Rich-based ArgumentParser with beautiful formatting"

# Main exports
__all__ = [
    # Main classes
    'RichArgumentParser',
    'CustomColoredArgumentParser',  # Backward compatibility
    
    # Configuration
    'Config',
    
    # Theme management
    'ThemeManager',
    
    # Internal components (for advanced users)
    'RichFormatter',
    'SmartHighlighter',
]

# Version info
version_info = tuple(map(int, __version__.split('.')))

def get_version():
    """Get the current version string."""
    return __version__

def list_presets():
    """List available theme presets."""
    return ThemeManager.list_presets()

def get_config_info():
    """Get information about available configuration options."""
    from dataclasses import fields
    
    config_fields = {}
    for field in fields(Config):
        config_fields[field.name] = {
            'type': field.type,
            'default': field.default,
            'description': _get_field_description(field.name)
        }
    
    return config_fields

def _get_field_description(field_name: str) -> str:
    """Get description for configuration field."""
    descriptions = {
        'indent': 'Line indentation for all content',
        'section_gap': 'Number of blank lines between sections',
        'dyn_format': 'Enable dynamic text highlighting (options, backticks, etc.)',
        'bullet_char': 'Character to use for bullet points in lists',
        'bullet_list': 'List of characters recognized as bullet points',
        'preserve_backticks': 'Keep backticks visible when highlighting backtick content',
        'max_width': 'Maximum terminal width (None for auto-detection)',
        'no_wrap_usage': 'Keep usage line unwrapped even if very long',
        'arg_column_width': 'Fixed width for argument/command column (None for auto-calculation)',
        'debug': 'Enable debug output for troubleshooting'
    }
    return descriptions.get(field_name, 'No description available')

# Quick usage example in module docstring
RichArgumentParser.__doc__ = """
A Rich-based ArgumentParser with beautiful colored output and simplified configuration.

Quick Examples:
    # Basic usage with preset theme
    parser = RichArgumentParser(
        prog="mytool",
        description="A CLI tool",
        theme="blue"
    )
    
    # Custom configuration
    config = Config(
        indent="    ",        # 4 spaces instead of 2
        bullet_char="→",      # Custom bullet
        section_gap=2         # More spacing
    )
    parser = RichArgumentParser(config=config, theme="green")
    
    # Method chaining
    parser = RichArgumentParser(prog="tool") \\
        .with_theme("purple") \\
        .with_config(dyn_format=True) \\
        .add_examples("tool --input file.txt") \\
        .add_pattern(r'\\bERROR\\b', 'red bold') \\
        .add_help_argument()

Available Themes:
    - default: Original color scheme
    - green: Nature-themed green palette  
    - blue: Ocean-themed blue palette
    - purple: Royal-themed purple/magenta palette
    
Configuration Options:
    - indent: Line indentation (default: "  ")
    - section_gap: Blank lines between sections (default: 1)
    - dyn_format: Dynamic text highlighting (default: True)
    - bullet_char: Bullet character (default: "•")
    - max_width: Terminal width override (default: None)
    - no_wrap_usage: Keep usage unwrapped (default: True)
    - debug: Debug output (default: False)

Features:
    - Table-based layout for perfect alignment
    - Dynamic option and program name highlighting
    - Custom sections (Examples, Notes, etc.)
    - Backtick syntax highlighting (`code`)
    - Custom regex patterns for highlighting
    - Simple INI-based themes
    - Method chaining for fluent configuration
"""