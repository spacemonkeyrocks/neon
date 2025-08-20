"""
Theme management for neon.
"""

import configparser
import os
from pathlib import Path
from typing import Dict, Union, Optional, List
from rich.theme import Theme
from rich.style import Style

from .exceptions import ThemeNotFoundError, NeonError


class ThemeManager:
    """Manages themes for Rich-based ArgumentParser."""
    
    # Default fallback theme (in case default.ini is missing)
    DEFAULT_THEME = {
        "argparse.args": "dark_cyan",
        "argparse.default": "white italic",
        "argparse.groups": "dark_orange3 bold",
        "argparse.help": "grey74",
        "argparse.metavar": "dark_green",
        "argparse.text": "grey74",
        "argparse.prog": "grey42",
        "argparse.syntax": "white italic bold",
        "error": "red",
        "warning": "dark_orange",
        "info": "blue",
        "success": "green"
    }
    
    @classmethod
    def _get_presets_dir(cls) -> Path:
        """Get the presets directory path."""
        return Path(__file__).parent / "presets"
    
    @classmethod
    def _load_preset_from_file(cls, preset_name: str) -> Optional[Dict[str, str]]:
        """
        Load a preset theme from INI file.
        
        Args:
            preset_name: Name of the preset (without .ini extension)
            
        Returns:
            Theme dictionary or None if not found
            
        Raises:
            ThemeNotFoundError: If preset file doesn't exist
            NeonError: If preset file is corrupted or invalid
        """
        presets_dir = cls._get_presets_dir()
        preset_file = presets_dir / f"{preset_name}.ini"
        
        if not preset_file.exists():
            raise ThemeNotFoundError(
                f"Preset theme '{preset_name}' not found. "
                f"Available presets: {cls.list_presets()}"
            )
        
        try:
            return cls._load_from_ini(preset_file)
        except Exception as e:
            raise NeonError(f"Failed to load preset '{preset_name}': {e}") from e
    
    @classmethod
    def load_theme(cls, theme: Union[str, Path, Dict, Theme]) -> Theme:
        """
        Load a theme from various sources.
        
        Args:
            theme: Theme name (preset), file path, dict, or Rich Theme object
            
        Returns:
            Rich Theme object
            
        Raises:
            ThemeNotFoundError: If theme file/preset cannot be found
            NeonError: If theme data is invalid or corrupted
        """
        if isinstance(theme, Theme):
            return theme
        
        if isinstance(theme, dict):
            try:
                # Validate that we can create a Rich theme from this dict
                return Theme(theme)
            except Exception as e:
                raise NeonError(f"Invalid theme dictionary: {e}") from e
        
        if isinstance(theme, (str, Path)):
            theme_str = str(theme)
            
            # Check if it's a preset name first
            try:
                preset_theme = cls._load_preset_from_file(theme_str)
                if preset_theme:
                    return Theme(preset_theme)
            except ThemeNotFoundError:
                # Not a preset, continue to check if it's a file path
                pass
            except NeonError:
                # Preset exists but is corrupted, re-raise
                raise
            
            # Check if it's a file path
            theme_path = Path(theme_str)
            if not theme_path.suffix:
                theme_path = theme_path.with_suffix('.ini')
            
            if theme_path.exists():
                try:
                    theme_dict = cls._load_from_ini(theme_path)
                    if theme_dict:
                        return Theme(theme_dict)
                except Exception as e:
                    raise NeonError(f"Failed to load theme from '{theme_path}': {e}") from e
            
            # Neither preset nor valid file path
            available_presets = cls.list_presets()
            raise ThemeNotFoundError(
                f"Theme '{theme}' not found. "
                f"Available presets: {available_presets}. "
                f"Or provide a valid .ini file path."
            )
        
        # Invalid theme type - fallback to default with warning
        try:
            return cls.load_theme("default")
        except ThemeNotFoundError:
            # Even default preset is missing, use hardcoded fallback
            return Theme(cls.DEFAULT_THEME)
    
    @classmethod
    def _load_from_ini(cls, file_path: Path) -> Optional[Dict[str, str]]:
        """
        Load theme from INI file.
        
        Args:
            file_path: Path to the INI file
            
        Returns:
            Theme dictionary or None if invalid
            
        Raises:
            NeonError: If file cannot be read or parsed
        """
        if not file_path.exists():
            raise NeonError(f"Theme file not found: {file_path}")
        
        try:
            config = configparser.ConfigParser()
            config.read(file_path, encoding='utf-8')
            
            if 'theme' not in config:
                raise NeonError(f"No [theme] section found in {file_path}")
            
            theme_dict = dict(config['theme'])
            
            # Validate that we have at least some required styles
            required_styles = ['argparse.args', 'argparse.groups', 'argparse.help']
            missing_styles = [style for style in required_styles if style not in theme_dict]
            
            if missing_styles:
                # Merge with default to ensure all styles are defined
                merged = cls.DEFAULT_THEME.copy()
                merged.update(theme_dict)
                return merged
            
            return theme_dict
            
        except configparser.Error as e:
            raise NeonError(f"Invalid INI file format in {file_path}: {e}") from e
        except Exception as e:
            raise NeonError(f"Error reading theme file {file_path}: {e}") from e
    
    @classmethod
    def save_theme(cls, theme: Theme, file_path: Union[str, Path]) -> None:
        """
        Save theme to INI file.
        
        Args:
            theme: Rich Theme object to save
            file_path: Path where to save the theme
            
        Raises:
            NeonError: If file cannot be written
        """
        try:
            config = configparser.ConfigParser()
            config['theme'] = {name: str(style) for name, style in theme.styles.items()}
            
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                config.write(f)
                
        except Exception as e:
            raise NeonError(f"Failed to save theme to {file_path}: {e}") from e
    
    @classmethod
    def list_presets(cls) -> List[str]:
        """
        List available preset names from the presets directory.
        
        Returns:
            List of preset names (without .ini extension)
        """
        presets_dir = cls._get_presets_dir()
        if not presets_dir.exists():
            return []
        
        presets = []
        for ini_file in presets_dir.glob("*.ini"):
            presets.append(ini_file.stem)  # filename without .ini extension
        
        return sorted(presets)
    
    @classmethod
    def get_preset_path(cls, name: str) -> Optional[Path]:
        """
        Get path to preset file if it exists.
        
        Args:
            name: Preset name (without .ini extension)
            
        Returns:
            Path to preset file or None if not found
        """
        presets_dir = cls._get_presets_dir()
        preset_file = presets_dir / f"{name}.ini"
        return preset_file if preset_file.exists() else None
    
    @classmethod
    def validate_theme_dict(cls, theme_dict: Dict[str, str]) -> bool:
        """
        Validate that a theme dictionary can create a valid Rich theme.
        
        Args:
            theme_dict: Dictionary of style names to style strings
            
        Returns:
            True if valid
            
        Raises:
            NeonError: If theme dictionary is invalid
        """
        try:
            # Try to create a Rich theme to validate styles
            Theme(theme_dict)
            return True
        except Exception as e:
            raise NeonError(f"Invalid theme styles: {e}") from e