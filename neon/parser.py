"""
Main RichArgumentParser class for neon.
"""

import argparse
from typing import Union, Optional, Dict, List, Any
from rich.theme import Theme

from .config import Config
from .theme import ThemeManager
from .formatter import RichFormatter


class RichHelpFormatter(argparse.HelpFormatter):
    """Argparse-compatible formatter that uses Rich for rendering."""
    
    def __init__(self, prog, indent_increment=2, max_help_position=24, width=None):
        super().__init__(prog, indent_increment, max_help_position, width)
        self._rich_formatter = None
        self._parser = None
    
    def _set_rich_formatter(self, rich_formatter: RichFormatter, parser):
        """Set the Rich formatter instance."""
        self._rich_formatter = rich_formatter
        self._parser = parser
    
    def format_help(self):
        """Format help using Rich formatter."""
        if self._rich_formatter:
            return self._rich_formatter.format_help()
        return super().format_help()


class RichArgumentParser(argparse.ArgumentParser):
    """
    ArgumentParser with Rich-based formatting and simplified configuration.
    
    Provides beautiful colored output with table-based layout, dynamic highlighting,
    and custom sections while maintaining full argparse compatibility.
    """
    
    def __init__(self,
                 prog: Optional[str] = None,
                 usage: Optional[str] = None,
                 description: Optional[str] = None,
                 epilog: Optional[str] = None,
                 parents: List = None,
                 formatter_class: type = None,
                 prefix_chars: str = '-',
                 fromfile_prefix_chars: Optional[str] = None,
                 argument_default: Any = None,
                 conflict_handler: str = 'error',
                 add_help: bool = True,
                 allow_abbrev: bool = True,
                 exit_on_error: bool = True,
                 # Library specific parameters
                 theme: Union[str, Dict, Theme] = "default",
                 config: Optional[Config] = None,
                 header: Optional[str] = None,
                 examples: Optional[Union[str, List[str]]] = None,
                 notes: Optional[Union[str, List[str]]] = None,
                 custom_patterns: Optional[Dict[str, str]] = None,
                 indent: Optional[int] = None,
                 section_gap: Optional[int] = None,
                 dyn_format: Optional[bool] = None,
                 bullet_char: Optional[str] = None,
                 bullet_list: Optional[List[str]] = None,
                 preserve_backticks: Optional[bool] = None,
                 max_width: Optional[int] = None,
                 no_wrap_usage: Optional[bool] = None,
                 arg_column_width: Optional[int] = None,
                 debug: Optional[bool] = None,
                 **kwargs):
        
        # Start with provided config or default
        if config is None:
            config = Config()
        
        # Merge any direct parameters into config
        config_updates = {}
        if theme != "default":  # Only override if explicitly set
            config_updates['theme'] = theme
        if header is not None:
            config_updates['header'] = header
        if examples is not None:
            config_updates['examples'] = examples
        if notes is not None:
            config_updates['notes'] = notes
        if custom_patterns is not None:
            config_updates['custom_patterns'] = custom_patterns
        if indent is not None:
            config_updates['indent'] = indent
        if section_gap is not None:
            config_updates['section_gap'] = section_gap
        if dyn_format is not None:
            config_updates['dyn_format'] = dyn_format
        if bullet_char is not None:
            config_updates['bullet_char'] = bullet_char
        if bullet_list is not None:
            config_updates['bullet_list'] = bullet_list
        if preserve_backticks is not None:
            config_updates['preserve_backticks'] = preserve_backticks
        if max_width is not None:
            config_updates['max_width'] = max_width
        if no_wrap_usage is not None:
            config_updates['no_wrap_usage'] = no_wrap_usage
        if arg_column_width is not None:
            config_updates['arg_column_width'] = arg_column_width
        if debug is not None:
            config_updates['debug'] = debug
        
        # Apply updates to config
        if config_updates:
            config = config.merge(**config_updates)
        
        # Store configuration
        self._config = config
        self._theme = ThemeManager.load_theme(config.theme)
        self._custom_patterns = config.custom_patterns or {}
        self._rich_formatter = None
        self._rich_formatter = None
        
        # Use custom formatter
        if formatter_class is None:
            formatter_class = RichHelpFormatter
        
        # Initialize parent ArgumentParser
        super().__init__(
            prog=prog,
            usage=usage,
            description=description,
            epilog=epilog,
            parents=parents or [],
            formatter_class=formatter_class,
            prefix_chars=prefix_chars,
            fromfile_prefix_chars=fromfile_prefix_chars,
            argument_default=argument_default,
            conflict_handler=conflict_handler,
            add_help=add_help,
            allow_abbrev=allow_abbrev,
            exit_on_error=exit_on_error,
            **kwargs
        )
        
        # Initialize Rich formatter
        self._rich_formatter = RichFormatter(self, self._config, self._theme)
        
        # Set up patterns
        if self._custom_patterns:
            self._rich_formatter.set_patterns(self._custom_patterns)
        
        # Set up custom content from config
        if config.header:
            self._rich_formatter.set_header(config.header)
        if config.examples:
            self.add_examples(config.examples)
        if config.notes:
            self.add_notes(config.notes)
    
    def _get_formatter(self):
        """Get formatter and set up Rich formatter reference."""
        formatter = super()._get_formatter()
        if hasattr(formatter, '_set_rich_formatter'):
            formatter._set_rich_formatter(self._rich_formatter, self)
        return formatter
    
    # Configuration methods (chainable)
    def with_theme(self, theme: Union[str, Dict, Theme]) -> 'RichArgumentParser':
        """Set theme. Returns self for method chaining."""
        self._theme = ThemeManager.load_theme(theme)
        self._rich_formatter = RichFormatter(self, self._config, self._theme)
        if self._custom_patterns:
            self._rich_formatter.set_patterns(self._custom_patterns)
        return self
    
    def with_config(self, **kwargs) -> 'RichArgumentParser':
        """Update configuration. Returns self for method chaining."""
        self._config = self._config.merge(**kwargs)
        self._rich_formatter = RichFormatter(self, self._config, self._theme)
        if self._custom_patterns:
            self._rich_formatter.set_patterns(self._custom_patterns)
        return self
    
    def configure(self, **kwargs) -> 'RichArgumentParser':
        """Alias for with_config for backward compatibility."""
        return self.with_config(**kwargs)
    
    # Content methods (chainable)
    def add_header(self, header: str) -> 'RichArgumentParser':
        """Add header text. Returns self for method chaining."""
        self._rich_formatter.set_header(header)
        return self
    
    def add_examples(self, examples: Union[str, List[str]]) -> 'RichArgumentParser':
        """Add examples section. Returns self for method chaining."""
        if isinstance(examples, list):
            examples = '\n'.join(examples)
        self._rich_formatter.add_custom_section("Examples", examples)
        return self
    
    def add_notes(self, notes: Union[str, List[str]]) -> 'RichArgumentParser':
        """Add notes section. Returns self for method chaining."""
        if isinstance(notes, list):
            notes = '\n'.join(notes)
        self._rich_formatter.add_custom_section("Notes", notes)
        return self
    
    def add_custom_section(self, title: str, content: Union[str, List[str]]) -> 'RichArgumentParser':
        """Add custom section. Returns self for method chaining."""
        if isinstance(content, list):
            content = '\n'.join(content)
        self._rich_formatter.add_custom_section(title, content)
        return self
    
    # Highlighting methods (chainable)
    def add_pattern(self, pattern: str, style: str) -> 'RichArgumentParser':
        """Add custom highlighting pattern. Returns self for method chaining."""
        self._custom_patterns[pattern] = style
        self._rich_formatter.add_pattern(pattern, style)
        return self
    
    def set_patterns(self, patterns: Dict[str, str]) -> 'RichArgumentParser':
        """Set custom highlighting patterns. Returns self for method chaining."""
        self._custom_patterns = patterns.copy()
        self._rich_formatter.set_patterns(patterns)
        return self
    
    def add_custom_pattern(self, pattern: str, style: str) -> 'RichArgumentParser':
        """Alias for add_pattern for backward compatibility."""
        return self.add_pattern(pattern, style)
    
    def set_custom_patterns(self, patterns: Dict[str, str]) -> 'RichArgumentParser':
        """Alias for set_patterns for backward compatibility."""
        return self.set_patterns(patterns)
    
    # Helper methods (chainable)
    def add_help_argument(self) -> 'RichArgumentParser':
        """Add help argument if not already present. Returns self for method chaining."""
        # Check if help argument already exists
        for action in self._actions:
            if isinstance(action, argparse._HelpAction):
                return self
        
        # Add help argument
        self.add_argument('-h', '--help', action='help', 
                         help='Show this help message and exit')
        return self
    
    # Information methods
    def get_config(self) -> Config:
        """Get current configuration."""
        return self._config
    
    def get_theme(self) -> Theme:
        """Get current theme."""
        return self._theme
    
    def list_presets(self) -> List[str]:
        """List available theme presets."""
        return ThemeManager.list_presets()


# Backward compatibility alias
CustomColoredArgumentParser = RichArgumentParser