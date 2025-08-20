"""
Rich-based help formatter for neon.
"""

import argparse
import re

from typing import List, Dict, Any, Optional, Union, Tuple

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.theme import Theme
from rich.markup import escape

from .config import Config
from .highlighting import SmartHighlighter


# Regex to strip rich styling tags
pattern = re.compile(r'\[(\/?)[^\]]+\]')

# Strip rich styling tags from any string
def strip_rich_tags(text):
    return pattern.sub('', text)

class RichFormatter:
    """Rich-based help formatter with table layout."""
    
    def __init__(self, parser, config: Config, theme: Theme):
        self.parser = parser
        self.config = config
        self.theme = theme
        self.highlighter = SmartHighlighter(parser, config)
        
        # Create console instances
        self.console = self._create_console()
        self.usage_console = self._create_console(no_wrap=True)
        
        # Custom sections storage
        self.custom_sections = {}
        self.header = None
        
        # Calculate argument column width
        self._calculated_arg_column_width: Optional[int] = None
    
    def _create_console(self, no_wrap: bool = False) -> Console:
        """Create a console instance with proper configuration."""
        width = self.config.max_width
        return Console(
            theme=self.theme,
            highlighter=self.highlighter if self.config.dyn_format else None,
            width=width,
            force_terminal=True,
            no_color=False,
            markup=True
        )
    
    def set_header(self, header: str) -> None:
        """Set header text."""
        self.header = header
    
    def add_custom_section(self, title: str, content: str) -> None:
        """Add a custom section."""
        self.custom_sections[title] = content
    
    def add_pattern(self, pattern: str, style: str) -> None:
        """Add custom highlighting pattern."""
        self.highlighter.add_pattern(pattern, style)
    
    def set_patterns(self, patterns: Dict[str, str]) -> None:
        """Set custom highlighting patterns."""
        self.highlighter.set_patterns(patterns)
    
    def format_help(self) -> str:
        """Format complete help message."""
        sections = []
        
        # Header
        if self.header:
            sections.append(self._format_header())
        
        # Usage
        usage = self._format_usage()
        if usage:
            sections.append(usage)
        
        # Description
        if self.parser.description:
            sections.append(self._format_description())
        
        # Subcommands
        subcommands_table = self._format_subcommands()
        if subcommands_table:
            sections.append(subcommands_table)
        
        # Argument groups
        group_tables = self._format_argument_groups()
        sections.extend(group_tables)
        
        # Custom sections
        custom_tables = self._format_custom_sections()
        sections.extend(custom_tables)
        
        # Epilog
        if self.parser.epilog:
            sections.append(self._format_epilog())
        
        # Join sections with spacing
        return self._join_sections(sections)
    
    def _format_header(self) -> str:
        """Format header section."""
        with self.console.capture() as capture:
            text = Text.from_markup(self.header)
            if self.config.dyn_format:
                self.highlighter.highlight(text)
            self.console.print(text, style="argparse.prog")
        return capture.get()
    
    def _format_usage(self) -> str:
        """Format usage line."""
        with self.usage_console.capture() as capture:
            usage_text = self._build_usage_text()
            text = Text.from_markup(usage_text)
            if self.config.dyn_format:
                self.highlighter.highlight(text)
            self.usage_console.print(text, style="argparse.text")
        return capture.get()
    
    def _build_usage_text(self) -> str:
        """Build usage line text."""
        parts = ["[argparse.groups]Usage:[/argparse.groups]"]
        
        # Program name
        prog = self.parser.prog or "program"
        parts.append(f"[argparse.prog]{prog}[/argparse.prog]")
        
        # Collect different argument types
        positional_args = []
        optional_args = []
        subcommands = []
        
        for action in self.parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                subcommands.append("[argparse.args]command[/argparse.args] [argparse.text]...[/argparse.text]")
                break
        
        for action in self.parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                continue
            elif action.option_strings:
                # Optional argument
                opt_str = action.option_strings[0]
                is_required = getattr(action, 'required', False)
                
                if action.metavar:
                    if is_required and self.config.debug:  # Use angle brackets for required if configured
                        part = f"<[argparse.args]{opt_str}[/argparse.args] [argparse.metavar]{action.metavar}[/argparse.metavar]>"
                    else:
                        part = f"\\[[argparse.args]{opt_str}[/argparse.args] [argparse.metavar]{action.metavar}[/argparse.metavar]]"
                else:
                    if is_required and self.config.debug:
                        part = f"<[argparse.args]{opt_str}[/argparse.args]>"
                    else:
                        part = f"\\[[argparse.args]{opt_str}[/argparse.args]]"
                optional_args.append(part)
            else:
                # Positional argument
                if action.dest == "help":
                    continue
                
                if action.metavar:
                    metavar = action.metavar
                elif action.dest != argparse.SUPPRESS:
                    metavar = action.dest.upper()
                else:
                    continue
                
                if action.nargs == "?":
                    part = f"\\[[argparse.metavar]{metavar}[/argparse.metavar]]"
                elif action.nargs == "*":
                    part = f"\\[[argparse.metavar]{metavar}[/argparse.metavar] [argparse.text]...[/argparse.text]]"
                elif action.nargs == "+":
                    part = f"[argparse.metavar]{metavar}[/argparse.metavar] \\[[argparse.metavar]{metavar}[/argparse.metavar] [argparse.text]...[/argparse.text]]"
                else:
                    part = f"[argparse.metavar]{metavar}[/argparse.metavar]"
                positional_args.append(part)
        
        # Combine all parts
        all_parts = parts + optional_args + positional_args + subcommands
        line = " ".join(all_parts)
        
        # If too long, insert line breaks at logical points
        if len(strip_rich_tags(line)) > (self.config.max_width or 80):
            return self._insert_smart_breaks(parts, optional_args, positional_args, subcommands)
        
        return line

    def _insert_smart_breaks(self, parts, optional_args, positional_args, subcommands):
        """Insert line breaks with dynamic continuation indentation."""
        # Calculate dynamic indentation based on "Usage: " + prog (+ command)
        usage_prefix_length = len(strip_rich_tags(" ".join(parts)))
        continuation_indent = " " * usage_prefix_length
        
        # Start with the initial parts (Usage: prog) 
        result = []
        result.extend(parts)  # ["Usage:", "prog"] or ["Usage:", "prog command"]
        
        # Track current line length (plain text)
        current_line_length = len(strip_rich_tags(" ".join(parts))) + 1  # +1 for space after prog
        
        # Add optional arguments
        for part in optional_args:
            part_length = len(strip_rich_tags(part))
            if current_line_length + part_length + 1 > (self.config.max_width or 80):
                # Start new line
                result.append(f"\n{continuation_indent}")
                current_line_length = len(continuation_indent)
            result.append(part)
            current_line_length += part_length + 1
        
        # Add positional arguments on new line if they exist
        if positional_args:
            result.append(f"\n{continuation_indent}")
            result.extend(positional_args)
        
        # Add subcommands on new line if they exist  
        if subcommands:
            result.append(f"\n{continuation_indent}")
            result.extend(subcommands)
        
        return " ".join(result)

    def _format_description(self) -> str:
        """Format description section."""
        with self.console.capture() as capture:
            text = Text.from_markup(self.parser.description)
            if self.config.dyn_format:
                self.highlighter.highlight(text)
            self.console.print(text, style="argparse.text")
        return capture.get()
    
    def _format_subcommands(self) -> Optional[str]:
        """Format subcommands section."""
        subparsers_action = None
        for action in self.parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                subparsers_action = action
                break
        
        if not subparsers_action or not subparsers_action.choices:
            return None
        
        with self.console.capture() as capture:
            title = getattr(subparsers_action, 'title', None) or "Commands"
            table = self._create_section_table(f"{title}:")
            
            for name, subparser in subparsers_action.choices.items():
                description = f"[argparse.text]{subparser.description}[/argparse.text]" if subparser.description else ""
                table.add_row("", f"[argparse.args]{name}[/argparse.args]", description)
            
            self.console.print(table)
        return capture.get()
    
    def _format_argument_groups(self) -> List[str]:
        """Format argument groups."""
        sections = []
        processed_groups = set()
        
        for group in self.parser._action_groups:
            # Skip default groups and empty groups
            if group.title in ['positional arguments', 'optional arguments']:
                continue
            
            # Filter out suppressed actions
            actions = [action for action in group._group_actions 
                      if action.help != argparse.SUPPRESS]
            
            if not actions:
                continue
            
            # Skip groups that contain subparsers (already handled)
            has_subparsers = any(isinstance(action, argparse._SubParsersAction) 
                               for action in actions)
            if has_subparsers:
                continue
            
            # Avoid duplicate groups
            if group.title in processed_groups:
                continue
            
            with self.console.capture() as capture:
                table = self._create_section_table(f"{group.title}:")
                
                for action in actions:
                    option_str = self._format_action_invocation(action)
                    help_text = self._format_action_help(action)
                    table.add_row("", option_str, help_text)
                
                self.console.print(table)
                processed_groups.add(group.title)
            
            sections.append(capture.get())
        
        return sections
    
    def _format_custom_sections(self) -> List[str]:
        """Format custom sections."""
        sections = []
        
        for title, content in self.custom_sections.items():
            with self.console.capture() as capture:
                # Create section header
                header_text = Text.from_markup(f"{title}:")
                self.console.print(header_text, style="argparse.groups")
                
                # Process content
                if isinstance(content, (list, tuple)):
                    content = "\n".join(str(item) for item in content)
                
                content_lines = str(content).strip().split('\n')
                
                # Check if content has bullet points
                has_bullets = any(self._is_bullet_line(line) for line in content_lines)
                
                if has_bullets:
                    # Create bullet table
                    table = Table(box=None, show_header=False, padding=0, pad_edge=False, style="argparse.text")
                    table.add_column(width=self.config.indent, no_wrap=True, style="argparse.text")   # Spacer
                    table.add_column(width=2, no_wrap=True, style="argparse.text")                    # Bullet
                    table.add_column(ratio=1, no_wrap=False, style="argparse.text")                   # Content
                    
                    for line in content_lines:
                        if line.strip():
                            if self._is_bullet_line(line):
                                bullet, text_content = self._extract_bullet(line)
                                formatted_text = self._format_text_content(text_content)
                                table.add_row("", bullet, formatted_text)
                            else:
                                formatted_text = self._format_text_content(line.strip())
                                table.add_row("", "", formatted_text)
                        else:
                            table.add_row("", "", "")
                    
                    self.console.print(table)
                else:
                    # Regular content table
                    table = Table(box=None, show_header=False, padding=0, pad_edge=False)
                    table.add_column(width=self.config.indent, no_wrap=True)   # Spacer
                    table.add_column(ratio=1, no_wrap=False)                   # Content
                    
                    for line in content_lines:
                        formatted_text = self._format_text_content(line)
                        table.add_row("", formatted_text)
                    
                    self.console.print(table)
            
            sections.append(capture.get())
        
        return sections
    
    def _format_epilog(self) -> str:
        """Format epilog section."""
        with self.console.capture() as capture:
            text = Text.from_markup(self.parser.epilog)
            if self.config.dyn_format:
                self.highlighter.highlight(text)
            self.console.print(text, style="argparse.text")
        return capture.get()
    
    def _create_section_table(self, title: str) -> Table:
        """Create a table for a section with header."""
        # Print title separately
        title_text = Text.from_markup(title)
        self.console.print(title_text, style="argparse.groups")
        
        # Lazily compute the width if needed
        if self.config.arg_column_width is None and self._calculated_arg_column_width is None:
            self._calculated_arg_column_width = self._calculate_max_arg_column_width()

        # Determine the width for the second column
        arg_col_width = self.config.arg_column_width or self._calculated_arg_column_width
        
        # Create table
        table = Table(box=None, show_header=False, padding=0, pad_edge=False)
        table.add_column(width=self.config.indent, no_wrap=True)   # Spacer
        table.add_column(width=arg_col_width, no_wrap=False)       # Options/Commands
        table.add_column(ratio=1, no_wrap=False)                   # Help text
        
        return table
    
    def _format_action_invocation(self, action) -> str:
        """Format action invocation (options + metavar)."""
        if not action.option_strings:
            # Positional argument
            if action.metavar:
                return f"[argparse.metavar]{action.metavar}[/argparse.metavar]"
            elif action.dest != argparse.SUPPRESS:
                return f"[argparse.metavar]{action.dest.upper()}[/argparse.metavar]"
            return ""
        
        # Optional argument
        option_parts = []
        for opt in action.option_strings:
            option_parts.append(f"[argparse.args]{opt}[/argparse.args]")
        
        option_str = ", ".join(option_parts)
        
        # Add extra spacing for long-only options
        if len(action.option_strings) == 1 and action.option_strings[0].startswith('--'):
            option_str = "    " + option_str
        
        # Add metavar if present
        if action.metavar:
            option_str += f" [argparse.metavar]{action.metavar}[/argparse.metavar]"
        
        return option_str
    
    def _format_action_help(self, action) -> str:
        """Format action help text."""
        help_text = action.help or ""
        if not help_text:
            return ""
        
        # Handle default values
        if (action.default is not None and 
            action.default != argparse.SUPPRESS):
        
            if '%(default)s' not in help_text:
                help_text += f" [argparse.default](default: {action.default})[/argparse.default]"
            else:
                # Replace %(default)s placeholder
                default_value = f"[argparse.default]{action.default}[/argparse.default]"
                help_text = help_text.replace('%(default)s', default_value)
        
        # Handle choices
        if action.choices:
            choices_str = ", ".join(str(choice) for choice in action.choices)
            
            if '%(choices)s' not in help_text:
                help_text += f" [argparse.metavar](choices: {choices_str})[/argparse.metavar]"
            else:
                choices_value = f"[argparse.metavar]{choices_str}[/argparse.metavar]"
                help_text = help_text.replace('%(choices)s', choices_value)        

        # Apply dynamic formatting if enabled
        if self.config.dyn_format:
            # Create Text object and apply highlighting
            text_obj = Text.from_markup(help_text, style="argparse.help")
            if self.config.dyn_format:
                self.highlighter.highlight(text_obj)
            # Convert back to markup string for table
            return text_obj.markup
        else:
            return f"{escape(help_text)}"
    
    def _format_text_content(self, text: str) -> str:
        """Format text content with proper styling."""
        if not text.strip():
            return ""
        
        # Apply dynamic formatting if enabled
        if self.config.dyn_format:
            # Create Text object and apply highlighting
            text_obj = Text.from_markup(text, style="argparse.text")
            if self.config.dyn_format:
                self.highlighter.highlight(text_obj)
            # Convert back to markup string for table
            return text_obj.markup
        else:
            return f"{escape(text)}"
    
    def _is_bullet_line(self, line: str) -> bool:
        """Check if line starts with a bullet character."""
        stripped = line.lstrip()
        if not stripped:
            return False
        
        return any(stripped.startswith(char + ' ') for char in self.config.bullet_list)
    
    def _extract_bullet(self, line: str) -> Tuple[str, str]:
        """Extract bullet and content from line."""
        stripped = line.lstrip()
        for char in self.config.bullet_list:
            if stripped.startswith(char + ' '):
                # Use bullet_char if specified, otherwise keep original
                display_bullet = self.config.bullet_char if self.config.bullet_char else char
                return display_bullet, stripped[2:]
        
        # Fallback
        fallback_bullet = self.config.bullet_char if self.config.bullet_char else '•'
        return fallback_bullet, stripped
    
    def _join_sections(self, sections: List[str]) -> str:
        """Join sections with proper spacing."""
        if not sections:
            return ""
        
        # Remove trailing whitespace from each section
        cleaned_sections = [section.rstrip() for section in sections if section.strip()]
        
        # Join with section gaps
        gap = '\n' * (self.config.section_gap + 1)
        return gap.join(cleaned_sections)
    
    def _calculate_max_arg_column_width(self) -> int:
        """
        Calculates the maximum width required for the second column (options/commands)
        across all argument groups and subcommands.
        """
        max_width = 0
        
        # First, handle subcommands
        for action in self.parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                for name in action.choices.keys():
                    width = len(name)
                    max_width = max(max_width, width)
        
        # Process all actions from all groups, but avoid duplicates
        all_actions = set()
        
        # Collect all actions from all groups
        for group in self.parser._action_groups:
            for action in group._group_actions:
                if (action.help != argparse.SUPPRESS and 
                    not isinstance(action, argparse._SubParsersAction)):
                    all_actions.add(action)
        
        # Now process each unique action
        for action in all_actions:
            # Format action invocation and measure its width
            option_str = self._format_action_invocation(action)
            if option_str:
                plain_option_str = strip_rich_tags(option_str)
                width = len(plain_option_str)
                
                # Get the option strings for better debugging
                if action.option_strings:
                    action_desc = ", ".join(action.option_strings)
                    if action.metavar:
                        action_desc += f" {action.metavar}"
                else:
                    action_desc = action.dest.upper() if action.dest != argparse.SUPPRESS else "unknown"
                
                max_width = max(max_width, width)
        
        # Add a small padding for aesthetics and ensure minimum width
        final_width = max(max_width + 3, 10)
        return final_width