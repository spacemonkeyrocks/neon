"""
Main NeonArgumentParser class for neon.
"""

import argparse

from typing import Union, Optional, Dict, List, Any
from rich.theme import Theme

from .config import NeonConfig
from .theme import NeonThemeManager
from .formatter import NeonFormatter


class NeonHelpFormatter(argparse.HelpFormatter):
    """Argparse-compatible formatter that uses Rich for rendering."""
    
    def __init__(self, prog, indent_increment=2, max_help_position=24, width=None):
        super().__init__(prog, indent_increment, max_help_position, width)
        self._rich_formatter = None
        self._parser = None
    
    def _set_rich_formatter(self, rich_formatter: NeonFormatter, parser):
        """Set the Rich formatter instance."""
        self._rich_formatter = rich_formatter
        self._parser = parser
    
    def format_help(self):
        """Format help using Rich formatter."""
        if self._rich_formatter:
            return self._rich_formatter.format_help()
        return super().format_help()


class _NeonArgumentGroup(argparse._ArgumentGroup):
    """Custom argument group that supports inheritance."""
    
    def __init__(self, container, title=None, description=None, inherit=False, **kwargs):
        super().__init__(container, title, description, **kwargs)
        self.inherit = inherit


class _NeonSubParsersAction(argparse._SubParsersAction):
    """Custom SubParsersAction that ensures subparsers inherit Neon formatting."""
    
    def add_parser(self, name, **kwargs):
        """Override to pass parent configuration to subparsers."""
        # Ensure subparsers inherit parent configuration
        if hasattr(self, '_parent_config'):
            kwargs.setdefault('_parent_config', self._parent_config)
        if hasattr(self, '_parent_theme'):
            kwargs.setdefault('_parent_theme', self._parent_theme)
        if hasattr(self, '_parent_custom_patterns'):
            kwargs.setdefault('_parent_custom_patterns', self._parent_custom_patterns)
        
        # Pass inherited groups and header
        if hasattr(self, '_parent_inherited_groups'):
            kwargs.setdefault('_parent_inherited_groups', self._parent_inherited_groups)
        if hasattr(self, '_parent_header'):
            kwargs.setdefault('_parent_header', self._parent_header)
        if hasattr(self, '_parent_add_help'):
            kwargs.setdefault('_parent_add_help', self._parent_add_help)
        
        # Use NeonArgumentParser as the parser class
        parser_class = kwargs.pop('parser_class', NeonArgumentParser)
        
        # Remove subparser-specific arguments that ArgumentParser doesn't accept
        help_text = kwargs.pop('help', None)
        aliases = kwargs.pop('aliases', [])
        
        # Create the subparser with proper prog name
        prog_name = f"{self._prog_prefix.rstrip(' ')}"  # Remove trailing space
        if not prog_name.endswith(name):
            prog_name = f"{prog_name} {name}"
        
        kwargs['prog'] = prog_name
        parser = parser_class(**kwargs)
        
        # Store the help text for the subparser
        if help_text:
            parser._help = help_text
        
        # Register the subparser
        self._name_parser_map[name] = parser
        return parser


class NeonArgumentParser(argparse.ArgumentParser):
    """
    ArgumentParser with Neon-based formatting and simplified configuration.
    
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
                 config: Optional[NeonConfig] = None,
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
                 error_prefix: Optional[str] = None,
                 # Internal parameters for subparser inheritance
                 _parent_config: Optional[NeonConfig] = None,
                 _parent_theme: Optional[Theme] = None,
                 _parent_custom_patterns: Optional[Dict[str, str]] = None,
                 _parent_inherited_groups: Optional[List] = None,
                 _parent_header: Optional[str] = None,
                 _parent_add_help: Optional[bool] = None,
                 **kwargs):
        
        # Start with provided config or default
        if config is None:
            config = NeonConfig()
        
        # Inherit from parent if this is a subparser
        if _parent_config is not None:
            config = _parent_config
        if theme == "default" and _parent_theme is not None:
            theme = _parent_theme
        if custom_patterns is None and _parent_custom_patterns is not None:
            custom_patterns = _parent_custom_patterns
        
        # Inherit header from parent if not explicitly set
        if header is None and _parent_header is not None:
            header = _parent_header
            
        # Inherit add_help from parent if this is a subparser and not explicitly set
        if _parent_add_help is not None and 'add_help' not in kwargs:
            add_help = _parent_add_help
        
        # Store the add_help setting for inheritance
        self._add_help = add_help
        
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
        if error_prefix is not None:
            config_updates['error_prefix'] = error_prefix
        
        # Apply updates to config
        if config_updates:
            config = config.merge(**config_updates)
        
        # Store configuration
        self._config = config
        self._theme = NeonThemeManager.load_theme(config.theme)
        self._custom_patterns = config.custom_patterns or {}
        self._rich_formatter = None
        self._inherited_groups = _parent_inherited_groups or []
        
        # Use custom formatter
        if formatter_class is None:
            formatter_class = NeonHelpFormatter
        
        # Initialize parent ArgumentParser first
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
        
        # Register custom subparsers action after parent init
        self.register('action', 'parsers', _NeonSubParsersAction)
        
        # Initialize Rich formatter
        self._rich_formatter = NeonFormatter(self, self._config, self._theme)
        
        # Set up patterns
        if self._custom_patterns:
            self._rich_formatter.set_patterns(self._custom_patterns)
        
        # Set up custom content from config (only for main parser, not inherited)
        if config.header and not _parent_config:
            self._rich_formatter.set_header(config.header)
        elif header and _parent_config:  # Inherited header
            self._rich_formatter.set_header(header)
            
        if config.examples and not _parent_config:
            self.add_examples(config.examples)
        if config.notes and not _parent_config:
            self.add_notes(config.notes)
        
        # Add inherited groups after initialization
        if self._inherited_groups:
            self._add_inherited_groups()
    
    def error(self, message):
        """Override error to use Rich formatting with NeonHighlighter."""
        from rich.console import Console
        from rich.text import Text
        
        console = Console(theme=self._theme)
        
        # Create the full error message with configurable prefix
        error_prefix = self._config.error_prefix
        full_message = f"{error_prefix} [argparse.text]{message}[/argparse.text]"
        
        # Apply highlighting to the entire message
        text = Text.from_markup(full_message)
        if self._config.dyn_format and self._rich_formatter and hasattr(self._rich_formatter, 'highlighter'):
            self._rich_formatter.highlighter.highlight(text)
        
        console.print(text)
        self.exit(2)
    
    def add_argument_group(self, title=None, description=None, inherit=False):
        """Override to support inherit parameter."""
        group = _NeonArgumentGroup(self, title, description, inherit=inherit)
        self._action_groups.append(group)
        return group
    
    def _add_inherited_groups(self):
        """Add inherited groups to this parser."""
        for group_info in self._inherited_groups:
            inherited_group = self.add_argument_group(
                title=group_info['title'],
                description=group_info['description']
            )
            
            # Add all actions from the inherited group
            for action_info in group_info['actions']:
                # Reconstruct the action
                args = action_info['args']
                kwargs = action_info['kwargs'].copy()  # Make a copy to avoid modifying original
                
                # Remove our custom 'action' key if it exists and handle it properly
                action_type = kwargs.pop('action', None)
                
                # Fix action types
                if action_type == 'storeaction':
                    # Default store action, don't specify action
                    pass
                elif action_type == 'count':
                    kwargs['action'] = 'count'
                elif action_type in ['store_true', 'store_false', 'store_const']:
                    kwargs['action'] = action_type
                
                # Handle positional vs optional arguments
                if args and not any(arg.startswith('-') for arg in args):
                    # Positional argument - use the dest name, not option strings
                    inherited_group.add_argument(args[0], **kwargs)
                else:
                    # Optional argument with option strings
                    inherited_group.add_argument(*args, **kwargs)
    
    def add_subparsers(self, **kwargs):
        """Override to ensure subparsers inherit Neon formatting."""
        # Set the parser_class to NeonArgumentParser for subparsers
        if 'parser_class' not in kwargs:
            kwargs['parser_class'] = type(self)
        
        # Store reference to parent config and theme for inheritance
        subparsers_action = super().add_subparsers(**kwargs)
        
        # Store parent configuration for inheritance
        subparsers_action._parent_config = self._config
        subparsers_action._parent_theme = self._theme
        subparsers_action._parent_custom_patterns = self._custom_patterns
        subparsers_action._parent_header = self._config.header
        subparsers_action._parent_add_help = self._add_help
        
        # Collect groups marked for inheritance
        inherited_groups = []
        for group in self._action_groups:
            if hasattr(group, 'inherit') and group.inherit:
                # Store group information
                group_info = {
                    'title': group.title,
                    'description': group.description,
                    'actions': []
                }
                
                # Store actions in the group
                for action in group._group_actions:
                    if action.help != argparse.SUPPRESS:
                        # Build kwargs more carefully
                        kwargs = {}
                        
                        # Basic attributes
                        if action.help:
                            kwargs['help'] = action.help
                        if action.metavar:
                            kwargs['metavar'] = action.metavar
                        if action.default != argparse.SUPPRESS and action.default is not None:
                            kwargs['default'] = action.default
                        if action.choices:
                            kwargs['choices'] = action.choices
                        if hasattr(action, 'required') and action.required:
                            kwargs['required'] = action.required
                        
                        # Handle different action types
                        if isinstance(action, argparse._CountAction):
                            kwargs['action'] = 'count'
                        elif isinstance(action, argparse._StoreTrueAction):
                            kwargs['action'] = 'store_true'
                        elif isinstance(action, argparse._StoreFalseAction):
                            kwargs['action'] = 'store_false'
                        elif isinstance(action, argparse._StoreConstAction):
                            kwargs['action'] = 'store_const'
                            kwargs['const'] = action.const
                        # For _StoreAction (default), don't specify action type
                        
                        # Handle action arguments
                        if action.option_strings:
                            # Optional argument
                            args = action.option_strings
                        else:
                            # Positional argument
                            args = [action.dest]
                        
                        action_info = {
                            'args': args,
                            'kwargs': kwargs
                        }
                        group_info['actions'].append(action_info)
                
                if group_info['actions']:  # Only add if group has actions
                    inherited_groups.append(group_info)
        
        subparsers_action._parent_inherited_groups = inherited_groups
        
        return subparsers_action
    
    def _get_formatter(self):
        """Get formatter and set up Rich formatter reference."""
        formatter = super()._get_formatter()
        if hasattr(formatter, '_set_rich_formatter'):
            formatter._set_rich_formatter(self._rich_formatter, self)
        return formatter
    
    # Configuration methods (chainable)
    def with_theme(self, theme: Union[str, Dict, Theme]) -> 'NeonArgumentParser':
        """Set theme. Returns self for method chaining."""
        self._theme = NeonThemeManager.load_theme(theme)
        self._rich_formatter = NeonFormatter(self, self._config, self._theme)
        if self._custom_patterns:
            self._rich_formatter.set_patterns(self._custom_patterns)
        return self
    
    def with_config(self, **kwargs) -> 'NeonArgumentParser':
        """Update configuration. Returns self for method chaining."""
        self._config = self._config.merge(**kwargs)
        self._rich_formatter = NeonFormatter(self, self._config, self._theme)
        if self._custom_patterns:
            self._rich_formatter.set_patterns(self._custom_patterns)
        return self
    
    # Content methods (chainable)
    def add_header(self, header: str) -> 'NeonArgumentParser':
        """Add header text. Returns self for method chaining."""
        self._rich_formatter.set_header(header)
        return self
    
    def add_examples(self, examples: Union[str, List[str]]) -> 'NeonArgumentParser':
        """Add examples section. Returns self for method chaining."""
        if isinstance(examples, list):
            examples = '\n'.join(examples)
        self._rich_formatter.add_custom_section("Examples", examples)
        return self
    
    def add_notes(self, notes: Union[str, List[str]]) -> 'NeonArgumentParser':
        """Add notes section. Returns self for method chaining."""
        if isinstance(notes, list):
            notes = '\n'.join(notes)
        self._rich_formatter.add_custom_section("Notes", notes)
        return self
    
    def add_custom_section(self, title: str, content: Union[str, List[str]]) -> 'NeonArgumentParser':
        """Add custom section. Returns self for method chaining."""
        if isinstance(content, list):
            content = '\n'.join(content)
        self._rich_formatter.add_custom_section(title, content)
        return self
    
    # Highlighting methods (chainable)
    def add_pattern(self, pattern: str, style: str) -> 'NeonArgumentParser':
        """Add custom highlighting pattern. Returns self for method chaining."""
        self._custom_patterns[pattern] = style
        self._rich_formatter.add_pattern(pattern, style)
        return self
    
    def set_patterns(self, patterns: Dict[str, str]) -> 'NeonArgumentParser':
        """Set custom highlighting patterns. Returns self for method chaining."""
        self._custom_patterns = patterns.copy()
        self._rich_formatter.set_patterns(patterns)
        return self
    
    # Helper methods (chainable)
    def add_help_argument(self) -> 'NeonArgumentParser':
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
    def get_config(self) -> NeonConfig:
        """Get current configuration."""
        return self._config
    
    def get_theme(self) -> Theme:
        """Get current theme."""
        return self._theme
    
    def list_presets(self) -> List[str]:
        """List available theme presets."""
        return NeonThemeManager.list_presets()