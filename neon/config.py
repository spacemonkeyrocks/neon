"""
Configuration system for neon.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Union
from rich.theme import Theme


@dataclass
class Config:
    """Configuration for RichArgumentParser formatting."""
    
    # Layout and formatting
    indent: int = 2                          # Line indentation
    section_gap: int = 1                     # Blank lines between sections
    max_width: Optional[int] = None          # Terminal width override
    no_wrap_usage: bool = True               # Keep usage line unwrapped
    arg_column_width: Optional[int] = None   # Fixed width for argument/command column
    
    # Text processing
    dyn_format: bool = True                  # Dynamic text highlighting
    preserve_backticks: bool = False         # Keep backticks when highlighting content
    
    # Bullet styling
    bullet_char: str = "•"                   # Standardize all bullets to this character (None to keep original)
    bullet_list: List[str] = \
        field(default_factory=lambda: ['•', '◦', '▪', '▫', '-', '*'])  # List of recognized bullet characters
   
    # Theme and styling
    theme: Union[str, Dict, Theme] = "default"  # Theme name, dict, or Rich Theme object
    custom_patterns: Optional[Dict[str, str]] = None  # Custom regex patterns for highlighting
    
    # Content sections
    header: Optional[str] = None             # Header text
    examples: Optional[Union[str, List[str]]] = None  # Examples section content
    notes: Optional[Union[str, List[str]]] = None     # Notes section content
    
    # Debug
    debug: bool = False                      # Debug output

    def __post_init__(self):
        """Validate and process fields after initialization."""
        # Type validation
        if not isinstance(self.indent, int):
            raise TypeError(f"indent must be int, got {type(self.indent).__name__}: {self.indent!r}")
        
        if not isinstance(self.section_gap, int):
            raise TypeError(f"section_gap must be int, got {type(self.section_gap).__name__}: {self.section_gap!r}")
        
        if self.max_width is not None and not isinstance(self.max_width, int):
            raise TypeError(f"max_width must be int or None, got {type(self.max_width).__name__}: {self.max_width!r}")
        
        if not isinstance(self.dyn_format, bool):
            raise TypeError(f"dyn_format must be bool, got {type(self.dyn_format).__name__}: {self.dyn_format!r}")
        
        if not isinstance(self.debug, bool):
            raise TypeError(f"debug must be bool, got {type(self.debug).__name__}: {self.debug!r}")
        
        # Initialize custom_patterns if None
        if self.custom_patterns is None:
            self.custom_patterns = {}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """Create Config from dictionary, ignoring unknown keys."""
        valid_fields = {field.name for field in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)
    
    def merge(self, **kwargs) -> 'Config':
        """Create new Config with updated values."""
        current_dict = self.__dict__.copy()
        current_dict.update(kwargs)
        return Config.from_dict(current_dict)